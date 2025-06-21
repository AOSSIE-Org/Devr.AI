-- Users
insert into
  users (
    id, created_at, updated_at, email, discord_id, discord_username,
    github_id, github_username, slack_id, slack_username, display_name,
    avatar_url, bio, location, is_verified, verification_token,
    verification_token_expires_at, verified_at, skills, github_stats,
    last_active_discord, last_active_github, last_active_slack,
    total_interactions_count, preferred_languages
  )
values
  (
    '6afc59e3-18b7-4182-b42c-8210d1152b07', '2025-05-05 03:56:41', '2025-01-22 14:50:25',
    'blakeerik@yahoo.com', '3eb13b9046684257', 'donaldgarcia', '16419f828b9d4434', 'fjohnson',
    '9a1de644815e46d1', 'hoffmanjennifer', 'Jennifer Cole', 'https://dummyimage.com/696x569',
    'Bill here grow gas enough analysis. Movie win her need stop peace technology.', 'East Steven',
    true, null, null, '2025-05-14 15:04:01',
    '{"skills": ["Python", "C++", "Java"]}'::jsonb, '{"commits": 300}'::jsonb,
    '2025-04-19 03:34:26', '2025-02-12 15:28:51', '2025-05-13 22:32:01', 28,
    array['JavaScript', 'C++']
  ),
  (
    '6f990423-0d57-4c64-b191-17e53f39c799', '2025-01-11 20:41:23', '2025-02-14 11:26:28',
    'jeffrey28@yahoo.com', '50c187fcce174b4e', 'nadams', 'e059a0ee9132463e', 'jason76',
    '757750a9a49140b2', 'josephwright', 'Deborah Richards', 'https://www.lorempixel.com/186/96',
    'Civil quite others his other life edge network. Quite boy those.', 'Kathrynside',
    true, null, null, '2025-01-01 02:39:54',
    '{"skills": ["C++", "TypeScript", "Rust"]}'::jsonb, '{"commits": 139}'::jsonb,
    '2025-04-27 07:17:02', '2025-03-04 22:40:36', '2025-04-05 21:04:03', 75,
    array['Go', 'Python']
  ),
  (
    '2aefee92-c7da-4d6e-90c1-d6c3bb82c0e1', '2025-03-01 17:07:10', '2025-02-16 11:55:43',
    'samuel87@gmail.com', '913e4de2e0c54cb8', 'millertodd', '885f6e66c2b642c5', 'davidalvarez',
    '8715a10343da4043', 'ibrandt', 'Melissa Marquez', 'https://www.lorempixel.com/507/460',
    'Open discover detail. Remain arrive attack all. Audience draw protect Democrat car very.', 'Stevenland',
    false, 'db20a56e-dc81-4fe7-8eda-8bbb71710434', '2025-06-21 12:00:00', null,
    '{"skills": ["Python", "JavaScript", "C++"]}'::jsonb, '{"commits": 567}'::jsonb,
    '2025-01-20 00:17:15', '2025-01-10 19:45:31', '2025-05-07 15:12:55', 77,
    array['Python', 'Rust']
  );

-- Repositories
insert into
  repositories (
    id, created_at, updated_at, github_id, full_name, name, owner, description,
    stars_count, forks_count, open_issues_count, languages_used, topics, is_indexed,
    indexed_at, indexing_status, last_commit_hash
  )
values
  (
    'f6b0bff9-074d-4062-86f5-0a853e521334', '2025-05-16 10:34:41', '2025-02-16 08:54:52', 3728882,
    'jamessellers/repo_0', 'repo_0', 'jamessellers', 'Him task improve fish list tree high.',
    3032, 363, 26, array['C++', 'Python'], array['Java', 'C++'], true, '2025-05-09 21:00:50',
    'completed', 'e270dbf424cff6864cc592f6611d8df90c895ec5'
  ),
  (
    '0f08ecdb-53dd-4352-bb50-b1cfbf09da8b', '2025-01-08 04:31:26', '2025-01-25 12:21:00', 3741438,
    'gallowayjoseph/repo_1', 'repo_1', 'gallowayjoseph', 'Whole forward beyond suddenly between treat address.',
    3786, 388, 34, array['C++', 'Go'], array['C++', 'Rust'], true, '2025-01-28 23:48:46',
    'completed', 'c9f97db5d2fc4b809df59bc23dd7345dbe6d14d5'
  ),
  (
    '08946f22-0d74-4499-b40d-0f60218d5152', '2025-04-02 03:59:05', '2025-02-21 11:05:44', 6292423,
    'fjohnson/repo_2', 'repo_2', 'fjohnson', 'Perhaps however bag forget purpose move.',
    3286, 274, 8, array['JavaScript', 'HTML'], array['Rust', 'C++'], false, '2025-03-03 11:44:52',
    'pending', '5e3af4aafc18e025cea707fa7707a1d945e0ffef'
  );

-- Interactions
insert into
  interactions (
    id, created_at, user_id, repository_id, platform, platform_specific_id, channel_id,
    thread_id, content, interaction_type, sentiment_score, intent_classification,
    topics_discussed, metadata
  )
values
  (
    '7c59fe66-53b6-44b5-8ae1-ddc29b071097', '2025-03-10 12:14:30', '6afc59e3-18b7-4182-b42c-8210d1152b07',
    'f6b0bff9-074d-4062-86f5-0a853e521334', 'github', 'aa143cd82ff34de4',
    'f982f4e08603456a', '86abd4e7f4124360',
    'Skill medical after them analysis hit health. Ground attack drop. Billion old series card good full poor store.',
    'comment', -0.07, 'help_request', array['C++', 'TypeScript'], '{"info": "capital"}'::jsonb
  ),
  (
    'f0c80815-fde1-4644-94ca-cd8915f11e46', '2025-03-19 16:14:11', '6f990423-0d57-4c64-b191-17e53f39c799',
    '0f08ecdb-53dd-4352-bb50-b1cfbf09da8b', 'github', '62fb26d7f4db4a07',
    '7f072cb92fd340c0', 'ec9f9c545e0a42ab',
    'Song risk bad own state. Family bill foreign fast knowledge response coach. Goal amount thank good your ever.',
    'pr', 0.6, 'help_request', array['JavaScript', 'TypeScript'], '{"info": "already"}'::jsonb
  ),
  (
    'ef139daa-fa4c-445a-8bf7-fdd725bdb82c', '2025-05-06 06:40:36', '2aefee92-c7da-4d6e-90c1-d6c3bb82c0e1',
    '08946f22-0d74-4499-b40d-0f60218d5152', 'slack', '9136f1f8f31046dc',
    'add702c92747493c', '5f3c44dc5ef747b8',
    'Off morning huge power. Whether ago control military trial. Energy employee land you.',
    'message', -0.16, 'feature_request', array['Go', 'JavaScript'], '{"info": "security"}'::jsonb
  );

-- Conversation Context
insert into
  conversation_context (
    id, user_id, platform, memory_thread_id, conversation_summary, key_topics,
    total_interactions, session_start_time, session_end_time, created_at
  )
values
  (
    'c1b2c3d4-e5f6-a7b8-c9d0-e1f2a3b4c5d6', '6afc59e3-18b7-4182-b42c-8210d1152b07',
    'discord', '112233445566778899',
    'The user asked about getting started with the API and had questions about authentication. They were provided with a link to the documentation.',
    array['onboarding', 'api_keys', 'authentication'], 8, '2025-06-20 10:00:00',
    '2025-06-20 10:25:00', '2025-06-20 10:25:00'
  ),
  (
    'd2c3d4e5-f6a7-b8c9-d0e1-f2a3b4c5d6e7', '6f990423-0d57-4c64-b191-17e53f39c799',
    'slack', '998877665544332211',
    'User reported a potential bug related to the repository indexing service. They provided logs and a repository URL. The issue was acknowledged and a ticket was created.',
    array['bug_report', 'indexing', 'repositories'], 12, '2025-06-21 09:00:00',
    '2025-06-21 09:45:00', '2025-06-21 09:45:00'
  ),
  (
    'e3d4e5f6-a7b8-c9d0-e1f2-a3b4c5d6e7f8', '2aefee92-c7da-4d6e-90c1-d6c3bb82c0e1',
    'discord', '123451234512345123',
    'A general discussion about the future of Rust and its use in web development. The user shared an article and asked for opinions.',
    array['Rust', 'web_development', 'discussion'], 5, '2025-06-19 14:30:00',
    '2025-06-19 15:00:00', '2025-06-19 15:00:00'
  );
