import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { StudentProfile } from '@/types/api';

interface AuthState {
  // Auth state
  profile: StudentProfile | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Actions
  setAuth: (profile: StudentProfile, token: string) => void;
  setProfile: (profile: StudentProfile) => void;
  updateProfile: (updates: Partial<StudentProfile>) => void;
  clearAuth: () => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      profile: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,

      setAuth: (profile, token) => {
        set({
          profile,
          token,
          isAuthenticated: true,
          isLoading: false
        });
      },

      setProfile: (profile) => {
        set({ profile });
      },

      updateProfile: (updates) => {
        const currentProfile = get().profile;
        if (currentProfile) {
          set({
            profile: { ...currentProfile, ...updates }
          });
        }
      },

      clearAuth: () => {
        set({
          profile: null,
          token: null,
          isAuthenticated: false,
          isLoading: false
        });
      },

      setLoading: (loading) => {
        set({ isLoading: loading });
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        profile: state.profile,
        token: state.token,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
);