import { useState, useEffect } from "react";
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
  useRegenerateAdminLessonContent,
  useVerifyAdminLesson,
} from "@/hooks/useApiQueries";
import {
  Plus,
  Edit,
  Trash2,
  Search,
  FileText,
  CheckCircle,
  Clock,
  RefreshCw,
  ArrowUpDown,
} from "lucide-react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Lesson } from "@/types/api";

const lessonSchema = z.object({
  title: z.string().min(1, "Lesson title is required"),
  language: z
    .enum([
      "Arabic",
      "English",
      "Pashto",
      "Persian",
      "Urdu",
    ])
    .default("Pashto"),
  content: z.string().optional(),
  subject_id: z.string().min(1, "Subject is required"),
});

type LessonFormData = z.infer<typeof lessonSchema>;

export const LessonManagement = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedSubject, setSelectedSubject] = useState<string>("");
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingLesson, setEditingLesson] = useState<Lesson | null>(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
  };

  const {
    data: subjects,
    isLoading: isLoadingSubjects,
    error: subjectsError,
  } = useAdminSubjects();
  const {
    data: lessons,
    isLoading: isLoadingLessons,
    error: lessonsError,
  } = useAdminLessons(selectedSubject);

  useEffect(() => {
    if (subjects && subjects.length > 0 && selectedSubject === "") {
      setSelectedSubject(subjects[0].id);
    }
  }, [subjects, selectedSubject]);

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    control,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(lessonSchema),
  });

  const createLessonMutation = useCreateAdminLesson();
  const updateLessonMutation = useUpdateAdminLesson();
  const deleteLessonMutation = useDeleteAdminLesson();
  const regenerateContentMutation = useRegenerateAdminLessonContent();
  const verifyLessonMutation = useVerifyAdminLesson();

  const filteredLessons = lessons?.filter(
    (lesson) =>
      lesson.title.toLowerCase().includes(searchTerm.toLowerCase()) &&
      (selectedSubject === "" || lesson.subject_id === selectedSubject)
  ) || [];

  const sortedLessons = [...filteredLessons].sort((a, b) => {
    if (!sortColumn) return 0;

    let aValue: any;
    let bValue: any;

    switch (sortColumn) {
      case "lesson":
        aValue = a.title.toLowerCase();
        bValue = b.title.toLowerCase();
        break;
      case "subject":
        aValue = subjects?.find((s) => s.id === a.subject_id)?.name?.toLowerCase() || "";
        bValue = subjects?.find((s) => s.id === b.subject_id)?.name?.toLowerCase() || "";
        break;
      case "language":
        aValue = a.language.toLowerCase();
        bValue = b.language.toLowerCase();
        break;
      case "status":
        aValue = a.status.toLowerCase();
        bValue = b.status.toLowerCase();
        break;
      case "created":
        aValue = new Date(a.created_at).getTime();
        bValue = new Date(b.created_at).getTime();
        break;
      default:
        return 0;
    }

    if (aValue < bValue) {
      return sortDirection === "asc" ? -1 : 1;
    }
    if (aValue > bValue) {
      return sortDirection === "asc" ? 1 : -1;
    }
    return 0;
  });

  const handleCreateLesson = async (data: LessonFormData) => {
    try {
      await createLessonMutation.mutateAsync({
        subjectId: data.subject_id,
        lessonData: { title: data.title, language: data.language },
      });
      setIsCreateModalOpen(false);
    } catch (error) {
      console.error("Failed to create lesson:", error);
    }
  };

  const handleEditLesson = (lesson: Lesson) => {
    setEditingLesson(lesson);
    setValue("title", lesson.title);
    setValue("language", lesson.language);
    setValue("content", lesson.content);
    setValue("subject_id", lesson.subject_id);
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
          subject_id: data.subject_id,
          language: data.language,
        },
      });
      setIsEditModalOpen(false);
      setEditingLesson(null);
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

  const handleRegenerateContent = async (lessonId: string) => {
    if (
      window.confirm(
        "Are you sure you want to regenerate content for this lesson?"
      )
    ) {
      try {
        await regenerateContentMutation.mutateAsync(lessonId);
      } catch (error) {
        console.error("Failed to regenerate lesson content:", error);
      }
    }
  };

  const handleVerifyLesson = async (lessonId: string) => {
    if (window.confirm("Are you sure you want to verify this lesson?")) {
      try {
        await verifyLessonMutation.mutateAsync(lessonId);
      } catch (error) {
        console.error("Failed to verify lesson:", error);
      }
    }
  };

  
  useEffect(() => {
    if (!isEditModalOpen) {
      setEditingLesson(null);
      reset();
    }
  }, [isEditModalOpen, reset]);

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
                <Controller
                  name="subject_id"
                  control={control}
                  render={({ field }) => (
                    <Select onValueChange={field.onChange} value={field.value}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a subject" />
                      </SelectTrigger>
                      <SelectContent>
                        {subjects
                          ?.filter(
                            (subject) =>
                              subject.id !== undefined && subject.id !== ""
                          )
                          .sort((a, b) => a.grade_level - b.grade_level)
                          .map((subject) => (
                            <SelectItem key={subject.id} value={subject.id}>
                              {subject.name} (Grade {subject.grade_level})
                            </SelectItem>
                          ))}
                      </SelectContent>
                    </Select>
                  )}
                />
                {errors.subject_id && (
                  <p className="text-sm text-destructive mt-1">
                    {errors.subject_id.message}
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
                <Label htmlFor="language">Language</Label>
                <Controller
                  name="language"
                  control={control}
                  render={({ field }) => (
                    <Select onValueChange={field.onChange} value={field.value}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select a language" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="English">English</SelectItem>
                        <SelectItem value="Pashto">Pashto</SelectItem>
                        <SelectItem value="Urdu">Urdu</SelectItem>
                        <SelectItem value="French">French</SelectItem>
                        <SelectItem value="Arabic">Arabic</SelectItem>
                        <SelectItem value="Spanish">Spanish</SelectItem>
                        <SelectItem value="Persian">Farsi</SelectItem>
                      </SelectContent>
                    </Select>
                  )}
                />
                {errors.language && (
                  <p className="text-sm text-destructive mt-1">
                    {errors.language.message}
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
              <Controller
                name="subject_id"
                control={control}
                render={({ field }) => (
                  <Select onValueChange={field.onChange} value={field.value}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a subject" />
                    </SelectTrigger>
                    <SelectContent>
                      {subjects
                        ?.filter(
                          (subject) =>
                            subject.id !== undefined && subject.id !== ""
                        )
                        .sort((a, b) => a.grade_level - b.grade_level)
                        .map((subject) => (
                          <SelectItem key={subject.id} value={subject.id}>
                            {subject.name} (Grade {subject.grade_level})
                          </SelectItem>
                        ))}
                    </SelectContent>
                  </Select>
                )}
              />
              {errors.subject_id && (
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
          onValueChange={(value) => setSelectedSubject(value)}
        >
          <SelectTrigger>
            <SelectValue placeholder="Filter by subject" />
          </SelectTrigger>
          <SelectContent>
            {subjects
              ?.filter(
                (subject) => subject.id !== undefined && subject.id !== ""
              )
              .sort((a, b) => a.grade_level - b.grade_level)
              .map((subject) => (
                <SelectItem key={subject.id} value={subject.id}>
                  {subject.name} (Grade {subject.grade_level})
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
                <TableHead>
                  <Button
                    variant="ghost"
                    onClick={() => handleSort("lesson")}
                    className="px-0 hover:bg-transparent"
                  >
                    Lesson
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                  </Button>
                </TableHead>
                <TableHead>
                  <Button
                    variant="ghost"
                    onClick={() => handleSort("subject")}
                    className="px-0 hover:bg-transparent"
                  >
                    Subject
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                  </Button>
                </TableHead>
                <TableHead>
                  <Button
                    variant="ghost"
                    onClick={() => handleSort("language")}
                    className="px-0 hover:bg-transparent"
                  >
                    Language
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                  </Button>
                </TableHead>
                <TableHead>
                  <Button
                    variant="ghost"
                    onClick={() => handleSort("status")}
                    className="px-0 hover:bg-transparent"
                  >
                    Status
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                  </Button>
                </TableHead>
                <TableHead>
                  <Button
                    variant="ghost"
                    onClick={() => handleSort("created")}
                    className="px-0 hover:bg-transparent"
                  >
                    Created
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                  </Button>
                </TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sortedLessons.map((lesson) => (
                <TableRow key={lesson.id}>
                  <TableCell>
                    <div>
                      <div className="font-medium flex items-center">
                        <FileText className="w-4 h-4 mr-2 text-primary" />
                        {lesson.title}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {lesson.content && lesson.content.length > 80
                          ? `${lesson.content.substring(0, 80)}...`
                          : lesson.content}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">
                      {subjects?.find((s) => s.id === lesson.subject_id)
                        ?.name || "N/A"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">
                      {lesson.language }
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center">
                      {lesson.status === "verified" ? (
                        <>
                          <CheckCircle className="w-4 h-4 mr-1 text-green-500 dark:text-green-400" />
                          <Badge variant="default">Verified</Badge>
                        </>
                      ) : (
                        // ) : lesson.status === "pending" ? (
                        //   <>
                        //     <Clock className="w-4 h-4 mr-1 text-blue-500" />
                        //     <Badge variant="secondary">Pending</Badge>
                        //   </>
                        // ) : lesson.status === "failed" ? (
                        //   <>
                        //     <XCircle className="w-4 h-4 mr-1 text-red-500" />
                        //     <Badge variant="destructive">Failed</Badge>
                        //   </>
                        <>
                          <Clock className="w-4 h-4 mr-1 text-yellow-500 dark:text-yellow-400" />
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
                        onClick={() => handleRegenerateContent(lesson.id)}
                        disabled={regenerateContentMutation.isPending}
                      >
                        <RefreshCw className="w-4 h-4" />
                      </Button>
                      {lesson.status !== "verified" && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleVerifyLesson(lesson.id)}
                          disabled={verifyLessonMutation.isPending}
                        >
                          <CheckCircle className="w-4 h-4" />
                        </Button>
                      )}
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
                    {selectedSubject && selectedSubject !== ""
                      ? `No lessons found for ${
                          subjects?.find((s) => s.id === selectedSubject)
                            ?.name || "this subject"
                        }.`
                      : "No lessons found. Select a subject to view lessons, or add a new lesson."}
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
