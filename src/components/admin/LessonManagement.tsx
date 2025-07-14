import React, { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  useAdminSubjects,
  useAdminLessons,
  useCreateAdminLesson,
  useUpdateAdminLesson,
  useDeleteAdminLesson,
} from "@/hooks/useApiQueries";
import {
  Plus,
  Edit,
  Trash2,
  Search,
  FileText,
  CheckCircle,
  Clock,
} from "lucide-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Lesson } from "@/types/api";

const lessonSchema = z.object({
  title: z.string().min(1, "Lesson title is required"),
  content: z.string().min(1, "Lesson content is required"),
  subjectId: z.string().min(1, "Subject is required"),
});

type LessonFormData = z.infer<typeof lessonSchema>;

export const LessonManagement = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedSubject, setSelectedSubject] = useState<string>("");
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingLesson, setEditingLesson] = useState<Lesson | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<LessonFormData>({
    resolver: zodResolver(lessonSchema),
  });

  const {
    data: subjects,
    isLoading: isLoadingSubjects,
    error: subjectsError,
  } = useAdminSubjects();
  const {
    data: lessons,
    isLoading: isLoadingLessons,
    error: lessonsError,
  } = useAdminLessons(selectedSubject === "" ? undefined : selectedSubject);

  const createLessonMutation = useCreateAdminLesson();
  const updateLessonMutation = useUpdateAdminLesson();
  const deleteLessonMutation = useDeleteAdminLesson();

  const filteredLessons =
    lessons?.filter(
      (lesson) =>
        lesson.title.toLowerCase().includes(searchTerm.toLowerCase()) &&
        (selectedSubject === "" || lesson.subjectId === selectedSubject)
    ) || [];

  const handleCreateLesson = async (data: LessonFormData) => {
    try {
      await createLessonMutation.mutateAsync({
        subjectId: data.subjectId,
        lessonData: { title: data.title, content: data.content },
      });
      setIsCreateModalOpen(false);
      reset();
    } catch (error) {
      console.error("Failed to create lesson:", error);
    }
  };

  const handleEditLesson = (lesson: Lesson) => {
    setEditingLesson(lesson);
    setValue("title", lesson.title);
    setValue("content", lesson.content);
    setValue("subjectId", lesson.subjectId);
    setIsEditModalOpen(true);
  };

  const handleUpdateLesson = async (data: LessonFormData) => {
    if (!editingLesson) return;
    try {
      await updateLessonMutation.mutateAsync({
        lessonId: editingLesson.id,
        lessonData: {
          title: data.title,
          content: data.content,
          subjectId: data.subjectId,
        },
      });
      setIsEditModalOpen(false);
      setEditingLesson(null);
      reset();
    } catch (error) {
      console.error("Failed to update lesson:", error);
    }
  };

  const handleDeleteLesson = async (lessonId: string) => {
    if (window.confirm("Are you sure you want to delete this lesson?")) {
      try {
        await deleteLessonMutation.mutateAsync(lessonId);
      } catch (error) {
        console.error("Failed to delete lesson:", error);
      }
    }
  };

  if (isLoadingSubjects || isLoadingLessons) {
    return (
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-10 w-32" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
        </div>
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-20 w-full" />
          ))}
        </div>
      </div>
    );
  }

  if (subjectsError || lessonsError) {
    return (
      <Alert variant="destructive">
        <AlertDescription>
          Failed to load lesson data. Please try again later.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Lesson Management</h2>
          <p className="text-muted-foreground">
            Create and manage educational lessons
          </p>
        </div>

        <Dialog open={isCreateModalOpen} onOpenChange={setIsCreateModalOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Add Lesson
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[600px]">
            <DialogHeader>
              <DialogTitle>Create New Lesson</DialogTitle>
              <DialogDescription>
                Add a new lesson to a subject in the platform.
              </DialogDescription>
            </DialogHeader>
            <form
              onSubmit={handleSubmit(handleCreateLesson)}
              className="space-y-4"
            >
              <div>
                <Label htmlFor="subjectId">Subject</Label>
                <Select onValueChange={(value) => setValue("subjectId", value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a subject" />
                  </SelectTrigger>
                  <SelectContent>
                    {subjects
                      ?.filter(
                        (subject) =>
                          subject.id !== undefined && subject.id !== ""
                      )
                      .map((subject) => (
                        <SelectItem key={subject.id} value={subject.id}>
                          {subject.name} (Grade {subject.grade_level})
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
                <p className="text-sm text-destructive mt-1">
                  Subject is required
                </p>
              </div>

              <div>
                <Label htmlFor="title">Lesson Title</Label>
                <Input
                  id="title"
                  {...register("title")}
                  placeholder="Introduction to..."
                />
                {errors.title && (
                  <p className="text-sm text-destructive mt-1">
                    {errors.title.message}
                  </p>
                )}
              </div>

              <div>
                <Label htmlFor="content">Lesson Content</Label>
                <Textarea
                  id="content"
                  {...register("content")}
                  placeholder="Detailed lesson content, objectives, and materials..."
                  rows={6}
                />
                {errors.content && (
                  <p className="text-sm text-destructive mt-1">
                    {errors.content.message}
                  </p>
                )}
              </div>

              <DialogFooter>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setIsCreateModalOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={isSubmitting || createLessonMutation.isPending}
                >
                  {createLessonMutation.isPending
                    ? "Creating..."
                    : "Create Lesson"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Edit Lesson Modal */}
      <Dialog open={isEditModalOpen} onOpenChange={setIsEditModalOpen}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>Edit Lesson</DialogTitle>
            <DialogDescription>
              Edit the details of the selected lesson.
            </DialogDescription>
          </DialogHeader>
          <form
            onSubmit={handleSubmit(handleUpdateLesson)}
            className="space-y-4"
          >
            <div>
              <Label htmlFor="subjectId">Subject</Label>
              <Select
                onValueChange={(value) => setValue("subjectId", value)}
                value={editingLesson?.subjectId}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a subject" />
                </SelectTrigger>
                <SelectContent>
                  {subjects
                    ?.filter(
                      (subject) => subject.id !== undefined && subject.id !== ""
                    )
                    .map((subject) => (
                      <SelectItem key={subject.id} value={subject.id}>
                        {subject.name} (Grade {subject.grade_level})
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
              {errors.subjectId && (
                <p className="text-sm text-destructive mt-1">
                  Subject is required
                </p>
              )}
            </div>

            <div>
              <Label htmlFor="title">Lesson Title</Label>
              <Input
                id="title"
                {...register("title")}
                placeholder="Introduction to..."
              />
              {errors.title && (
                <p className="text-sm text-destructive mt-1">
                  {errors.title.message}
                </p>
              )}
            </div>

            <div>
              <Label htmlFor="content">Lesson Content</Label>
              <Textarea
                id="content"
                {...register("content")}
                placeholder="Detailed lesson content, objectives, and materials..."
                rows={6}
              />
              {errors.content && (
                <p className="text-sm text-destructive mt-1">
                  {errors.content.message}
                </p>
              )}
            </div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsEditModalOpen(false)}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={isSubmitting || updateLessonMutation.isPending}
              >
                {updateLessonMutation.isPending
                  ? "Updating..."
                  : "Update Lesson"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <Input
            placeholder="Search lessons by title..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>

        <Select
          value={selectedSubject}
          onValueChange={(value) =>
            setSelectedSubject(value === "all" ? "" : value)
          }
        >
          <SelectTrigger>
            <SelectValue placeholder="Filter by subject" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Subjects</SelectItem>
            {subjects
              ?.filter(
                (subject) => subject.id !== undefined && subject.id !== ""
              )
              .map((subject) => (
                <SelectItem key={subject.id} value={subject.id}>
                  {subject.name}
                </SelectItem>
              ))}
          </SelectContent>
        </Select>
      </div>

      {/* Lessons Table */}
      <Card>
        <CardHeader>
          <CardTitle>Lessons ({filteredLessons.length})</CardTitle>
          <CardDescription>
            Manage educational lessons and their content
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Lesson</TableHead>
                <TableHead>Subject</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Created</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredLessons.map((lesson) => (
                <TableRow key={lesson.id}>
                  <TableCell>
                    <div>
                      <div className="font-medium flex items-center">
                        <FileText className="w-4 h-4 mr-2 text-primary" />
                        {lesson.title}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {lesson.content.length > 80
                          ? `${lesson.content.substring(0, 80)}...`
                          : lesson.content}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">
                      {subjects?.find((s) => s.id === lesson.subjectId)?.name ||
                        "N/A"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center">
                      {lesson.status === "VE" ? (
                        <>
                          <CheckCircle className="w-4 h-4 mr-1 text-green-500" />
                          <Badge variant="default">Verified</Badge>
                        </>
                      ) : (
                        <>
                          <Clock className="w-4 h-4 mr-1 text-yellow-500" />
                          <Badge variant="secondary">Draft</Badge>
                        </>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm text-muted-foreground">
                      {new Date(lesson.created_at).toLocaleDateString()}
                    </div>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleEditLesson(lesson)}
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-destructive hover:text-destructive"
                        onClick={() => handleDeleteLesson(lesson.id)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
              {filteredLessons.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8">
                    No lessons found
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};
