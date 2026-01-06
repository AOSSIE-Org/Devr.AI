export interface PullRequest {
  number: number;
  title: string;
  author: {
    login: string;
    avatar_url: string;
    profile_url: string;
  };
  state: string;
  url: string;
  comments?: number;
  created_at?: string;
}

export interface RepositoryData {
  id: string;
  name: string;
  full_name: string;
  description?: string;
  html_url: string;
  stargazers_count: number;
  forks_count: number;
  language?: string;
  created_at: string;
  updated_at: string;
  owner: {
    login: string;
    avatar_url: string;
  };
  contributors?: any[];
  pull_requests?: {
    open: number;
    total: number;
    details?: PullRequest[];
  };
}
