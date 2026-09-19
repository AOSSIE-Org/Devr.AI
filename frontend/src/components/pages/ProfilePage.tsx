import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { User, Mail, Building, Globe, Github, Twitter, Edit, Camera, Save, Loader2, AlertCircle, RefreshCw } from 'lucide-react';
import { apiClient, ProfileResponse } from '../../lib/api';

interface ProfileState {
  name: string;
  role: string;
  company: string;
  email: string;
  website: string;
  github: string;
  twitter: string;
  bio: string;
  avatar_url: string;
}

const DEFAULT_AVATAR = 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200';

const EMPTY_PROFILE: ProfileState = {
  name: '',
  role: 'Core Maintainer',
  company: '',
  email: '',
  website: '',
  github: '',
  twitter: '',
  bio: '',
  avatar_url: DEFAULT_AVATAR,
};

const ProfilePage = () => {
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [profile, setProfile] = useState<ProfileState>(EMPTY_PROFILE);
  const [originalProfile, setOriginalProfile] = useState<ProfileState>(EMPTY_PROFILE);

  const mapResponseToState = (data: ProfileResponse): ProfileState => {
    return {
      name: data.display_name ?? data.name ?? '',
      role: data.role ?? data.skills?.role ?? 'Core Maintainer',
      company: data.company ?? data.skills?.company ?? '',
      email: data.email ?? '',
      website: data.website ?? data.skills?.website ?? '',
      github: data.github ?? (data.skills?.github ? data.skills.github : ''),
      twitter: data.twitter ?? data.skills?.twitter ?? '',
      bio: data.bio ?? '',
      avatar_url: data.avatar_url ?? DEFAULT_AVATAR,
    };
  };

  const fetchProfile = useCallback(async () => {
    try {
      setIsLoading(true);
      setLoadError(null);
      const data = await apiClient.getProfile();
      if (data) {
        const loadedProfile = mapResponseToState(data);
        setProfile(loadedProfile);
        setOriginalProfile(loadedProfile);
      }
    } catch (error: any) {
      console.error('Failed to fetch profile:', error);
      const message = error?.response?.data?.detail || 'Failed to load profile. Please verify your connection and try again.';
      setLoadError(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  const handleSave = async () => {
    if (loadError) return;
    try {
      setIsSaving(true);
      const updated = await apiClient.updateProfile({
        display_name: profile.name,
        name: profile.name,
        email: profile.email,
        bio: profile.bio,
        company: profile.company,
        website: profile.website,
        github: profile.github,
        twitter: profile.twitter,
        role: profile.role,
        avatar_url: profile.avatar_url,
      });

      const updatedState = mapResponseToState(updated);
      setProfile(updatedState);
      setOriginalProfile(updatedState);
      setIsEditing(false);
      toast.success('Profile updated successfully!');
    } catch (error: any) {
      console.error('Failed to update profile:', error);
      const message = error?.response?.data?.detail || 'Failed to update profile. Please try again.';
      toast.error(message);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setProfile(originalProfile);
    setIsEditing(false);
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto flex flex-col items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 text-green-500 animate-spin mb-4" />
        <p className="text-gray-400 text-sm">Loading profile...</p>
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="max-w-4xl mx-auto flex flex-col items-center justify-center min-h-[400px] text-center p-6 bg-gray-900 rounded-xl border border-red-800/50">
        <AlertCircle className="w-12 h-12 text-red-500 mb-4" />
        <h2 className="text-xl font-semibold text-white mb-2">Unable to Load Profile</h2>
        <p className="text-gray-400 text-sm max-w-md mb-6">{loadError}</p>
        <button
          onClick={fetchProfile}
          className="px-4 py-2 bg-green-500 hover:bg-green-600 rounded-lg transition-colors flex items-center text-white text-sm font-medium"
        >
          <RefreshCw size={16} className="mr-2" />
          Retry Loading
        </button>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="max-w-4xl mx-auto"
    >
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">Profile</h1>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          disabled={isSaving || Boolean(loadError)}
          onClick={() => {
            if (isEditing) {
              handleSave();
            } else {
              setIsEditing(true);
            }
          }}
          className="px-4 py-2 bg-green-500 hover:bg-green-600 disabled:opacity-50 rounded-lg transition-colors flex items-center"
        >
          {isSaving ? (
            <>
              <Loader2 size={18} className="mr-2 animate-spin" />
              Saving...
            </>
          ) : isEditing ? (
            <>
              <Save size={18} className="mr-2" />
              Save Changes
            </>
          ) : (
            <>
              <Edit size={18} className="mr-2" />
              Edit Profile
            </>
          )}
        </motion.button>
      </div>

      <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
        <div className="h-48 bg-gradient-to-r from-green-600 to-green-400 relative">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="absolute bottom-4 right-4 p-2 bg-black/20 hover:bg-black/40 rounded-lg text-white"
          >
            <Camera size={20} />
          </motion.button>
        </div>

        <div className="px-8 pb-8">
          <div className="flex items-end -mt-12 mb-8">
            <div className="relative">
              <img
                src={profile.avatar_url || DEFAULT_AVATAR}
                alt="Profile"
                className="w-24 h-24 rounded-xl border-4 border-gray-900 object-cover"
              />
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="absolute bottom-2 right-2 p-1.5 bg-gray-900 hover:bg-gray-800 rounded-lg text-white border border-gray-700"
              >
                <Camera size={14} />
              </motion.button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Full Name</label>
                <div className="flex items-center space-x-3">
                  <User size={20} className="text-gray-400 flex-shrink-0" />
                  <input
                    type="text"
                    value={profile.name}
                    onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                    disabled={!isEditing}
                    className="bg-transparent text-white focus:outline-none disabled:opacity-50 w-full"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Email</label>
                <div className="flex items-center space-x-3">
                  <Mail size={20} className="text-gray-400 flex-shrink-0" />
                  <input
                    type="email"
                    value={profile.email}
                    onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                    disabled={!isEditing}
                    className="bg-transparent text-white focus:outline-none disabled:opacity-50 w-full"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Company</label>
                <div className="flex items-center space-x-3">
                  <Building size={20} className="text-gray-400 flex-shrink-0" />
                  <input
                    type="text"
                    value={profile.company}
                    onChange={(e) => setProfile({ ...profile, company: e.target.value })}
                    disabled={!isEditing}
                    className="bg-transparent text-white focus:outline-none disabled:opacity-50 w-full"
                  />
                </div>
              </div>
            </div>

            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Website</label>
                <div className="flex items-center space-x-3">
                  <Globe size={20} className="text-gray-400 flex-shrink-0" />
                  <input
                    type="url"
                    value={profile.website}
                    onChange={(e) => setProfile({ ...profile, website: e.target.value })}
                    disabled={!isEditing}
                    className="bg-transparent text-white focus:outline-none disabled:opacity-50 w-full"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">GitHub</label>
                <div className="flex items-center space-x-3">
                  <Github size={20} className="text-gray-400 flex-shrink-0" />
                  <input
                    type="text"
                    value={profile.github}
                    onChange={(e) => setProfile({ ...profile, github: e.target.value })}
                    disabled={!isEditing}
                    className="bg-transparent text-white focus:outline-none disabled:opacity-50 w-full"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Twitter</label>
                <div className="flex items-center space-x-3">
                  <Twitter size={20} className="text-gray-400 flex-shrink-0" />
                  <input
                    type="text"
                    value={profile.twitter}
                    onChange={(e) => setProfile({ ...profile, twitter: e.target.value })}
                    disabled={!isEditing}
                    className="bg-transparent text-white focus:outline-none disabled:opacity-50 w-full"
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="mt-8">
            <label className="block text-sm font-medium text-gray-400 mb-2">Bio</label>
            <textarea
              value={profile.bio}
              onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
              disabled={!isEditing}
              rows={4}
              className="w-full bg-gray-800 rounded-lg p-3 text-white focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
            />
          </div>
          {isEditing && (
            <div className="mt-8 flex justify-end space-x-4">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                disabled={isSaving}
                onClick={handleCancel}
                className="px-4 py-2 bg-gray-800 hover:bg-gray-700 disabled:opacity-50 rounded-lg transition-colors"
              >
                Cancel
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                disabled={isSaving}
                onClick={handleSave}
                className="px-4 py-2 bg-green-500 hover:bg-green-600 disabled:opacity-50 rounded-lg transition-colors flex items-center"
              >
                {isSaving ? (
                  <>
                    <Loader2 size={18} className="mr-2 animate-spin" />
                    Saving...
                  </>
                ) : (
                  'Save Changes'
                )}
              </motion.button>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default ProfilePage;