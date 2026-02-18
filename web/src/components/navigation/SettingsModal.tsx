import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Label } from "../ui/label";
// import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../ui/select";
// import { Button } from "../ui/button";
// import { useForm } from "react-hook-form";
// import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
// import { useStudentProfile, useUpdateStudentProfile, useLanguages } from "@/hooks/useApiQueries";
import { Switch } from "../ui/switch";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "@/providers/ThemeProvider";

const studentProfileSchema = z.object({
  language: z.string(),
});

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SettingsModal = ({ isOpen, onClose }: SettingsModalProps) => {

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Settings</DialogTitle>
        </DialogHeader>
        <SettingsForm onClose={onClose} />
      </DialogContent>
    </Dialog>
  );
};

const SettingsForm = ({ onClose }) => {
  // const { data: profile } = useStudentProfile();
  // const { data: languages } = useLanguages();
  // const updateStudentProfileMutation = useUpdateStudentProfile();
  const { theme, setTheme } = useTheme();

  // const { handleSubmit: handleStudentSubmit, setValue: setStudentValue } = useForm({
  //   resolver: zodResolver(studentProfileSchema),
  //   values: {
  //     language: profile?.student_profile?.language || "",
  //   },
  // });

  // const onStudentSubmit = (data: any) => {
  //   updateStudentProfileMutation.mutate(data);
  //   onClose();
  // };

  return (
    <div className="space-y-6 py-4">
      <div className="flex items-center justify-between">
        <Label htmlFor="theme-mode" className="flex items-center gap-2">
          {theme === "dark" ? <Moon /> : <Sun />}
          <span>Theme Mode</span>
        </Label>
        <Switch
          id="theme-mode"
          checked={theme === "dark"}
          onCheckedChange={() => setTheme(theme === "dark" ? "light" : "dark")}
        />
      </div>
      {/* <form onSubmit={handleStudentSubmit(onStudentSubmit)} className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="language">Language</Label>
          <Select
            onValueChange={(value) => setStudentValue("language", value)}
            defaultValue={profile?.student_profile?.language}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select a language" />
            </SelectTrigger>
            <SelectContent>
              {languages?.map((lang: string) => (
                <SelectItem key={lang} value={lang}>
                  {lang}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <Button type="submit" disabled={updateStudentProfileMutation.isPending}>
          {updateStudentProfileMutation.isPending
            ? "Saving..."
            : "Save Changes"}
        </Button>
      </form> */}
    </div>
  );
};