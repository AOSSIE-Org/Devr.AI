import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { User, Mail, MapPin, Edit, Camera, Save, X } from 'lucide-react';
import { apiClient, UserProfile, UserProfileUpdateRequest } from '../../lib/api';

const ProfilePage = () => {
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [editedProfile, setEditedProfile] = useState<UserProfileUpdateRequest>({});

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    setIsLoading(true);
    try {
      const userProfile = await apiClient.getUserProfile();
      setProfile(userProfile);
      // Initialize edited profile with current values
      setEditedProfile({
        display_name: userProfile.display_name,
        bio: userProfile.bio || '',
        location: userProfile.location || '',
        avatar_url: userProfile.avatar_url || '',
        preferred_languages: userProfile.preferred_languages || []
      });
    } catch (error) {
      console.error('Error loading profile:', error);
      toast.error('Failed to load profile');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    if (!profile) return;
    
    setIsSaving(true);
    try {
      const updatedProfile = await apiClient.updateUserProfile(editedProfile);
      setProfile(updatedProfile);
      setIsEditing(false);
      toast.success('Profile updated successfully!');
    } catch (error) {
      console.error('Error updating profile:', error);
      toast.error('Failed to update profile');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    // Reset edited profile to current profile values
    if (profile) {
      setEditedProfile({
        display_name: profile.display_name,
        bio: profile.bio || '',
        location: profile.location || '',
        avatar_url: profile.avatar_url || '',
        preferred_languages: profile.preferred_languages || []
      });
    }
    setIsEditing(false);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading profile...</p>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-red-400">Failed to load profile</p>
          <button
            onClick={loadProfile}
            className="mt-4 px-4 py-2 bg-green-500 hover:bg-green-600 rounded-lg transition-colors"
          >
            Retry
          </button>
        </div>
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
        {!isEditing ? (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setIsEditing(true)}
            className="px-4 py-2 bg-green-500 hover:bg-green-600 rounded-lg transition-colors flex items-center"
          >
            <Edit size={18} className="mr-2" />
            Edit Profile
          </motion.button>
        ) : (
          <div className="flex gap-2">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleCancel}
              disabled={isSaving}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors flex items-center disabled:opacity-50"
            >
              <X size={18} className="mr-2" />
              Cancel
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleSave}
              disabled={isSaving}
              className="px-4 py-2 bg-green-500 hover:bg-green-600 rounded-lg transition-colors flex items-center disabled:opacity-50"
            >
              <Save size={18} className="mr-2" />
              {isSaving ? 'Saving...' : 'Save Changes'}
            </motion.button>
          </div>
        )}
      </div>

      <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
        <div className="h-48 bg-gradient-to-r from-green-600 to-green-400 relative">
          {isEditing && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="absolute bottom-4 right-4 p-2 bg-black/20 hover:bg-black/40 rounded-lg text-white"
              title="Upload banner (coming soon)"
            >
              <Camera size={20} />
            </motion.button>
          )}
        </div>

        <div className="px-8 pb-8">
          <div className="flex items-end -mt-12 mb-8">
            <div className="relative">
              <img
                src={profile.avatar_url || `https://ui-avatars.com/api/?name=${encodeURIComponent(profile.display_name)}&size=200&background=10b981&color=fff`}
                alt="Profile"
                className="w-24 h-24 rounded-xl border-4 border-gray-900 object-cover"
              />
              {isEditing && (
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="absolute bottom-2 right-2 p-1.5 bg-gray-900 hover:bg-gray-800 rounded-lg text-white border border-gray-700"
                  title="Upload avatar (coming soon)"
                >
                  <Camera size={14} />
                </motion.button>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Display Name *</label>
                <div className="flex items-center space-x-3">
                  <User size={20} className="text-gray-400 flex-shrink-0" />
                  {isEditing ? (
                    <input
                      type="text"
                      value={editedProfile.display_name || ''}
                      onChange={(e) => setEditedProfile({ ...editedProfile, display_name: e.target.value })}
                      className="flex-1 bg-gray-800 text-white px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                      placeholder="Enter your name"
                    />
                  ) : (
                    <span className="text-white">{profile.display_name}</span>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Email <span className="text-xs">(non-editable)</span>
                </label>
                <div className="flex items-center space-x-3">
                  <Mail size={20} className="text-gray-400 flex-shrink-0" />
                  <span className="text-white opacity-70">{profile.email || 'Not provided'}</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Location</label>
                <div className="flex items-center space-x-3">
                  <MapPin size={20} className="text-gray-400 flex-shrink-0" />
                  {isEditing ? (
                    <input
                      type="text"
                      value={editedProfile.location || ''}
                      onChange={(e) => setEditedProfile({ ...editedProfile, location: e.target.value })}
                      className="flex-1 bg-gray-800 text-white px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                      placeholder="City, Country"
                    />
                  ) : (
                    <span className="text-white">{profile.location || 'Not specified'}</span>
                  )}
                </div>
              </div>
            </div>

            <div className="space-y-6">
              {profile.github_username && (
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">GitHub Username</label>
                  <div className="flex items-center space-x-3">
                    <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                      <path fillRule="evenodd" d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.17 6.839 9.49.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.463-1.11-1.463-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0112 6.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.167 22 16.418 22 12c0-5.523-4.477-10-10-10z" clipRule="evenodd" />
                    </svg>
                    <span className="text-white">{profile.github_username}</span>
                  </div>
                </div>
              )}

              {profile.discord_username && (
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">Discord Username</label>
                  <div className="flex items-center space-x-3">
                    <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515a.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0a12.64 12.64 0 0 0-.617-1.25a.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057a19.9 19.9 0 0 0 5.993 3.03a.078.078 0 0 0 .084-.028a14.09 14.09 0 0 0 1.226-1.994a.076.076 0 0 0-.041-.106a13.107 13.107 0 0 1-1.872-.892a.077.077 0 0 1-.008-.128a10.2 10.2 0 0 0 .372-.292a.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127a12.299 12.299 0 0 1-1.873.892a.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028a19.839 19.839 0 0 0 6.002-3.03a.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419c0-1.333.956-2.419 2.157-2.419c1.21 0 2.176 1.096 2.157 2.42c0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419c0-1.333.955-2.419 2.157-2.419c1.21 0 2.176 1.096 2.157 2.42c0 1.333-.946 2.418-2.157 2.418z"/>
                    </svg>
                    <span className="text-white">{profile.discord_username}</span>
                  </div>
                </div>
              )}

              {profile.slack_username && (
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">Slack Username</label>
                  <div className="flex items-center space-x-3">
                    <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165a2.527 2.527 0 0 1 2.522-2.52h2.52v2.52zM6.313 15.165a2.527 2.527 0 0 1 2.521-2.52a2.527 2.527 0 0 1 2.521 2.52v6.313A2.528 2.528 0 0 1 8.834 24a2.528 2.528 0 0 1-2.521-2.522v-6.313zM8.834 5.042a2.528 2.528 0 0 1-2.521-2.52A2.528 2.528 0 0 1 8.834 0a2.528 2.528 0 0 1 2.521 2.522v2.52H8.834zM8.834 6.313a2.528 2.528 0 0 1 2.521 2.521a2.528 2.528 0 0 1-2.521 2.521H2.522A2.528 2.528 0 0 1 0 8.834a2.528 2.528 0 0 1 2.522-2.521h6.312zM18.956 8.834a2.528 2.528 0 0 1 2.522-2.521A2.528 2.528 0 0 1 24 8.834a2.528 2.528 0 0 1-2.522 2.521h-2.522V8.834zM17.688 8.834a2.528 2.528 0 0 1-2.523 2.521a2.527 2.527 0 0 1-2.52-2.521V2.522A2.527 2.527 0 0 1 15.165 0a2.528 2.528 0 0 1 2.523 2.522v6.312zM15.165 18.956a2.528 2.528 0 0 1 2.523 2.522A2.528 2.528 0 0 1 15.165 24a2.527 2.527 0 0 1-2.52-2.522v-2.522h2.52zM15.165 17.688a2.527 2.527 0 0 1-2.52-2.523a2.526 2.526 0 0 1 2.52-2.52h6.313A2.527 2.527 0 0 1 24 15.165a2.528 2.528 0 0 1-2.522 2.523h-6.313z"/>
                    </svg>
                    <span className="text-white">{profile.slack_username}</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="mt-8">
            <label className="block text-sm font-medium text-gray-400 mb-2">Bio</label>
            {isEditing ? (
              <textarea
                value={editedProfile.bio || ''}
                onChange={(e) => setEditedProfile({ ...editedProfile, bio: e.target.value })}
                rows={4}
                className="w-full bg-gray-800 rounded-lg p-3 text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="Tell us about yourself..."
              />
            ) : (
              <p className="text-white bg-gray-800 rounded-lg p-3 min-h-[100px]">
                {profile.bio || 'No bio provided yet.'}
              </p>
            )}
          </div>

          {profile.preferred_languages && profile.preferred_languages.length > 0 && (
            <div className="mt-8">
              <label className="block text-sm font-medium text-gray-400 mb-2">Preferred Languages</label>
              <div className="flex flex-wrap gap-2">
                {profile.preferred_languages.map((lang) => (
                  <span
                    key={lang}
                    className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm"
                  >
                    {lang}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default ProfilePage;
