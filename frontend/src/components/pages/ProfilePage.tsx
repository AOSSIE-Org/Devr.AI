import { useState, useEffect, useRef } from 'react'; // Added useRef
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import {
    User,
    Mail,
    Edit,
    Camera,
    Save,
    MessageSquare,
    CheckCircle,
    XCircle,
    Trash2,
    Loader2,
    Code,
    Layers,
} from 'lucide-react';
import { supabase } from '../../lib/supabaseClient';
import { API_BASE_URL } from '../../lib/api';
import SkillSection from '../ui/skills';

interface SkillsData {
    languages: string[];
    frameworks: string[];
}

interface UserProfile {
    display_name: string;
    email: string;
    bio: string;
    avatar_url: string;
    avatar_path: string;
    discord: string;
    github: string;
    slack: string;
    skills: SkillsData;
}

const GithubIcon = ({
    size = 20,
    className = '',
}: {
    size?: number;
    className?: string;
}) => (
    <svg
        width={size}
        height={size}
        viewBox="0 0 24 24"
        fill="currentColor"
        className={className}
        xmlns="http://www.w3.org/2000/svg"
    >
        <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405 1.02 0 2.04.135 3 .405 2.28-1.56 3.285-1.23 3.285-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
    </svg>
);

const SlackIcon = ({
    size = 20,
    className = '',
}: {
    size?: number;
    className?: string;
}) => (
    <svg
        width={size}
        height={size}
        viewBox="0 0 24 24"
        fill="currentColor"
        className={className}
        xmlns="http://www.w3.org/2000/svg"
    >
        <path d="M5.042 15.123a2.52 2.52 0 0 1 2.52-2.52h2.52v2.52a2.52 2.52 0 0 1-5.04 0zm0-5.04a2.52 2.52 0 0 1 2.52 2.52v2.52h-2.52a2.52 2.52 0 1 1 0-5.04zm5.04 0a2.52 2.52 0 0 1 2.52-2.52h2.52v2.52a2.52 2.52 0 0 1-5.04 0zm5.04 0a2.52 2.52 0 0 1-2.52-2.52v-2.52h2.52a2.52 2.52 0 0 1 0 5.04zM8.82 10.083a2.52 2.52 0 0 1-2.52 2.52H3.78v-2.52a2.52 2.52 0 0 1 5.04 0zm5.04 5.04a2.52 2.52 0 0 1-2.52-2.52v-2.52h2.52a2.52 2.52 0 0 1 0 5.04zm0-5.04a2.52 2.52 0 0 1 2.52 2.52v2.52h-2.52a2.52 2.52 0 0 1 0-5.04zm5.04 5.04a2.52 2.52 0 0 1-2.52-2.52v-2.52h2.52a2.52 2.52 0 0 1 0 5.04z" />
    </svg>
);

const ProfilePage = () => {
    const [isEditing, setIsEditing] = useState(false);
    const [loading, setLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [uploadingAvatar, setUploadingAvatar] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const [newLanguage, setNewLanguage] = useState('');
    const [newFramework, setNewFramework] = useState('');

    const [profile, setProfile] = useState<UserProfile>({
        display_name: '',
        email: '',
        bio: '',
        avatar_url: '',
        avatar_path: '',
        discord: '',
        github: '',
        slack: '',
        skills: { languages: [], frameworks: [] },
    });

    useEffect(() => {
        const fetchProfileData = async () => {
            try {
                const {
                    data: { session },
                    error: sessionError,
                } = await supabase.auth.getSession();
                if (sessionError || !session) {
                    toast.error('Please log in to view your profile');
                    return;
                }

                const token = session.access_token;
                const response = await fetch(`${API_BASE_URL}/v1/profile/`, {
                    method: 'GET',
                    headers: {
                        Authorization: `Bearer ${token}`,
                        'Content-Type': 'application/json',
                    },
                });

                if (!response.ok)
                    throw new Error('Failed to fetch profile data');

                const data = await response.json();

                if (data && data.user) {
                    let parsedSkills: SkillsData = {
                        languages: [],
                        frameworks: [],
                    };

                    if (
                        data.user.skills &&
                        typeof data.user.skills === 'object' &&
                        !Array.isArray(data.user.skills)
                    ) {
                        parsedSkills = {
                            languages: Array.isArray(data.user.skills.languages)
                                ? data.user.skills.languages
                                : [],
                            frameworks: Array.isArray(
                                data.user.skills.frameworks
                            )
                                ? data.user.skills.frameworks
                                : [],
                        };
                    }

                    setProfile((prev) => ({
                        ...prev,
                        display_name: data.user.display_name || '',
                        email: data.user.email || '',
                        bio: data.user.bio || '',
                        avatar_url: data.user.avatar_url || '',
                        avatar_path: data.user.avatar_path || '',
                        discord: data.user.discord || '',
                        github: data.user.github || '',
                        slack: data.user.slack || '',
                        skills: parsedSkills,
                    }));
                }
            } catch (error) {
                console.error('Error loading profile:', error);
                toast.error('Failed to load profile data');
            } finally {
                setLoading(false);
            }
        };
        fetchProfileData();
    }, []);

    const handleAvatarUpload = async (
        event: React.ChangeEvent<HTMLInputElement>
    ) => {
        try {
            if (!event.target.files || event.target.files.length === 0) {
                return;
            }
            if (profile.avatar_path) {
                await supabase.storage
                    .from('avatars')
                    .remove([profile.avatar_path]);
            }

            const file = event.target.files[0];
            const fileExt = file.name.split('.').pop();
            const fileName = `${Math.random()}.${fileExt}`;
            const filePath = `${fileName}`;

            setUploadingAvatar(true);
            const { error: uploadError } = await supabase.storage
                .from('avatars')
                .upload(filePath, file);

            if (uploadError) {
                throw uploadError;
            }
            const {
                data: { publicUrl },
            } = supabase.storage.from('avatars').getPublicUrl(filePath);
            setProfile((prev) => ({
                ...prev,
                avatar_url: publicUrl,
                avatar_path: filePath,
            }));
            toast.success("Image uploaded! Click 'Save Changes' to apply.");
        } catch (error: any) {
            console.error('Error uploading avatar:', error);
            toast.error('Error uploading image');
        } finally {
            setUploadingAvatar(false);
        }
    };

    const handleRemoveAvatar = async () => {
        if (!profile.avatar_path) return;
        const { error } = await supabase.storage
            .from('avatars')
            .remove([profile.avatar_path]);
        if (error) {
            throw error;
        }
        setProfile((prev) => ({ ...prev, avatar_url: '' ,avatar_path: ''}));
        toast.success("Avatar removed. Click 'Save Changes' to apply.");
    };

    const triggerFileInput = () => {
        if (fileInputRef.current) {
            fileInputRef.current.click();
        }
    };

    const handleSave = async () => {
        setIsSaving(true);
        try {
            const {
                data: { session },
            } = await supabase.auth.getSession();
            if (!session) {
                toast.error('You must be logged in to save changes.');
                setIsSaving(false);
                return;
            }
            const token = session.access_token;

            const payload = {
                display_name: profile.display_name,
                bio: profile.bio,
                avatar_url: profile.avatar_url,
                avatar_path: profile.avatar_path,
                discord: profile.discord,
                github: profile.github,
                slack: profile.slack,
                skills: profile.skills,
            };

            const response = await fetch(`${API_BASE_URL}/v1/profile/edit`, {
                method: 'PATCH',
                headers: {
                    Authorization: `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to update profile');
            }

            toast.success('Profile updated successfully!');
            setIsEditing(false);
        } catch (error: any) {
            console.error('Error saving profile:', error);
            toast.error(error.message || 'Failed to save changes');
        } finally {
            setIsSaving(false);
        }
    };

    const addSkill = (type: 'languages' | 'frameworks', value: string) => {
        if (value.trim()) {
            if (!profile.skills[type].includes(value.trim())) {
                setProfile((prev) => ({
                    ...prev,
                    skills: {
                        ...prev.skills,
                        [type]: [...prev.skills[type], value.trim()],
                    },
                }));
            }
            if (type === 'languages') setNewLanguage('');
            else setNewFramework('');
        }
    };

    const removeSkill = (
        type: 'languages' | 'frameworks',
        skillToRemove: string
    ) => {
        setProfile((prev) => ({
            ...prev,
            skills: {
                ...prev.skills,
                [type]: prev.skills[type].filter((s) => s !== skillToRemove),
            },
        }));
    };

    const renderSocialField = (
        icon: React.ReactNode,
        value: string,
        field: keyof UserProfile,
        placeholder: string
    ) => (
        <div className="flex items-center space-x-3 h-10">
            {icon}
            {isEditing ? (
                <input
                    type="text"
                    value={value as string}
                    onChange={(e) =>
                        setProfile({ ...profile, [field]: e.target.value })
                    }
                    className="bg-transparent text-white focus:outline-none border-b border-gray-700 focus:border-green-500 w-full pb-1 transition-colors"
                    placeholder={placeholder}
                />
            ) : (
                <div className="flex items-center">
                    {value ? (
                        <span className="flex items-center text-green-400 text-sm font-medium bg-green-400/10 px-3 py-1 rounded-full border border-green-400/20">
                            <CheckCircle size={14} className="mr-1.5" />
                            Connected
                        </span>
                    ) : (
                        <span className="flex items-center text-gray-500 text-sm font-medium bg-gray-800 px-3 py-1 rounded-full border border-gray-700">
                            <XCircle size={14} className="mr-1.5" />
                            Not Connected
                        </span>
                    )}
                </div>
            )}
        </div>
    );

    if (loading)
        return (
            <div className="text-white text-center mt-20 animate-pulse">
                Loading profile...
            </div>
        );

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-4xl mx-auto"
        >
            <div className="flex items-center justify-between mb-8">
                <h1 className="text-3xl font-bold">Profile</h1>
                <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={isEditing ? handleSave : () => setIsEditing(true)}
                    disabled={isSaving || uploadingAvatar}
                    className={`px-4 py-2 rounded-lg transition-colors flex items-center ${
                        isEditing
                            ? 'bg-green-500 hover:bg-green-600 text-white'
                            : 'bg-gray-800 hover:bg-gray-700 text-gray-200'
                    }`}
                >
                    {isSaving ? (
                        'Saving...'
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
                <div className="h-48 bg-gradient-to-r from-green-600 to-green-400 relative"></div>

                <div className="px-8 pb-8">
                    <div className="flex items-end -mt-12 mb-8">
                        <div className="relative group">
                            {/* The Image */}
                            <img
                                src={
                                    profile.avatar_url ||
                                    'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200'
                                }
                                alt="Profile"
                                className="w-24 h-24 rounded-xl border-4 border-gray-900 object-cover bg-gray-800"
                            />

                            {uploadingAvatar && (
                                <div className="absolute inset-0 bg-black/50 flex items-center justify-center rounded-xl z-20">
                                    <Loader2
                                        className="animate-spin text-green-500"
                                        size={24}
                                    />
                                </div>
                            )}

                            {isEditing && (
                                <>
                                    <input
                                        type="file"
                                        ref={fileInputRef}
                                        onChange={handleAvatarUpload}
                                        accept="image/*"
                                        className="hidden"
                                    />

                                    {/* Upload Button */}
                                    <motion.button
                                        whileHover={{ scale: 1.05 }}
                                        whileTap={{ scale: 0.95 }}
                                        onClick={triggerFileInput}
                                        className="absolute bottom-2 right-2 p-1.5 bg-gray-900 hover:bg-gray-800 rounded-lg text-white border border-gray-700 shadow-lg z-10"
                                        title="Change Avatar"
                                    >
                                        <Camera size={14} />
                                    </motion.button>

                                    {/* Remove Button */}
                                    {profile.avatar_url && (
                                        <motion.button
                                            whileHover={{ scale: 1.05 }}
                                            whileTap={{ scale: 0.95 }}
                                            onClick={handleRemoveAvatar}
                                            className="absolute top-2 right-[-40px] p-1.5 bg-red-500/20 hover:bg-red-500/40 rounded-lg text-red-400 border border-red-500/30 shadow-lg z-10"
                                            title="Remove Avatar"
                                        >
                                            <Trash2 size={14} />
                                        </motion.button>
                                    )}
                                </>
                            )}
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div className="space-y-6">
                            {/* Display Name */}
                            <div>
                                <label className="block text-sm font-medium text-gray-400 mb-2">
                                    Display Name
                                </label>
                                <div className="flex items-center space-x-3">
                                    <User size={20} className="text-gray-400" />
                                    <input
                                        type="text"
                                        value={profile.display_name}
                                        onChange={(e) =>
                                            setProfile({
                                                ...profile,
                                                display_name: e.target.value,
                                            })
                                        }
                                        disabled={!isEditing}
                                        className={`bg-transparent text-white focus:outline-none w-full ${isEditing ? 'border-b border-gray-700 pb-1 focus:border-green-500' : ''}`}
                                        placeholder="Enter display name"
                                    />
                                </div>
                            </div>

                            {/* Email */}
                            <div>
                                <label className="block text-sm font-medium text-gray-400 mb-2">
                                    Email
                                </label>
                                <div className="flex items-center space-x-3">
                                    <Mail size={20} className="text-gray-400" />
                                    <input
                                        type="email"
                                        value={profile.email}
                                        readOnly
                                        className="bg-transparent text-gray-400 w-full cursor-not-allowed"
                                    />
                                </div>
                            </div>

                            {/* Languages Section */}
                            <SkillSection
                                title="Languages"
                                icon={<Code size={20} />}
                                items={profile.skills.languages}
                                type="languages"
                                inputValue={newLanguage}
                                setInputValue={setNewLanguage}
                                isEditing={isEditing}
                                onAdd={addSkill}
                                onRemove={removeSkill}
                            />

                            {/* Frameworks Section */}
                            <SkillSection
                                title="Frameworks"
                                icon={<Layers size={20} />}
                                items={profile.skills.frameworks}
                                type="frameworks"
                                inputValue={newFramework}
                                setInputValue={setNewFramework}
                                isEditing={isEditing}
                                onAdd={addSkill}
                                onRemove={removeSkill}
                            />
                        </div>

                        <div className="space-y-6">
                            <div>
                                <label className="block text-sm font-medium text-gray-400 mb-2">
                                    GitHub
                                </label>
                                {renderSocialField(
                                    <GithubIcon
                                        size={20}
                                        className="text-gray-400"
                                    />,
                                    profile.github,
                                    'github',
                                    'Username'
                                )}
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-400 mb-2">
                                    Discord
                                </label>
                                {renderSocialField(
                                    <MessageSquare
                                        size={20}
                                        className="text-gray-400"
                                    />,
                                    profile.discord,
                                    'discord',
                                    'ID/Tag'
                                )}
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-400 mb-2">
                                    Slack
                                </label>
                                {renderSocialField(
                                    <SlackIcon
                                        size={20}
                                        className="text-gray-400"
                                    />,
                                    profile.slack,
                                    'slack',
                                    'ID'
                                )}
                            </div>
                        </div>
                    </div>

                    <div className="mt-8">
                        <label className="block text-sm font-medium text-gray-400 mb-2">
                            Bio
                        </label>
                        <textarea
                            value={profile.bio || ''}
                            onChange={(e) =>
                                setProfile({ ...profile, bio: e.target.value })
                            }
                            disabled={!isEditing}
                            rows={4}
                            placeholder="Tell us about yourself..."
                            className={`w-full bg-gray-800 rounded-lg p-3 text-white focus:outline-none disabled:opacity-60 ${isEditing ? 'focus:ring-2 focus:ring-green-500' : ''}`}
                        />
                    </div>

                    {isEditing && (
                        <div className="mt-8 flex justify-end space-x-4">
                            <button
                                onClick={() => setIsEditing(false)}
                                className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-white"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleSave}
                                disabled={isSaving || uploadingAvatar}
                                className="px-4 py-2 bg-green-500 hover:bg-green-600 rounded-lg text-white"
                            >
                                {isSaving ? 'Saving...' : 'Save Changes'}
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </motion.div>
    );
};

export default ProfilePage;
