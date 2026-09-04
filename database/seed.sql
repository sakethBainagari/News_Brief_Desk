insert into users (name, email, role)
values
  ('Saketh', 'saketh@example.com', 'REPORTER'),
  ('Rahul', 'rahul@example.com', 'EDITOR'),
  ('Priya', 'priya@example.com', 'DESK_HEAD')
on conflict (email) do nothing;

insert into raw_items (source_name, headline, body, category, source_published_at)
values
(
  'Deccan Business Wire',
  'Hyderabad semiconductor facility receives government approval',
  'Authorities have cleared a proposed $2 billion semiconductor manufacturing facility in Hyderabad. The project is expected to create thousands of direct and indirect jobs after construction begins.',
  'Technology',
  now() - interval '20 hours'
),
(
  'South Asia Technology Review',
  'Government clears $2bn chip plant planned for Hyderabad',
  'A major chip manufacturing project in Hyderabad has received government clearance, according to officials familiar with the approval. The proposed investment is valued at approximately $2 billion.',
  'Technology',
  now() - interval '19 hours'
),
(
  'Metro Press Network',
  'Hyderabad set for major semiconductor investment after project clearance',
  'Hyderabad is set to receive a large semiconductor investment after authorities approved plans for a manufacturing facility worth about $2 billion.',
  'Technology',
  now() - interval '18 hours'
),
(
  'Capital Markets Daily',
  'Bengaluru research center gets $800m technology commitment',
  'A separate technology research center planned in Bengaluru has secured an $800 million investment commitment. The project is focused on advanced semiconductor research rather than manufacturing.',
  'Technology',
  now() - interval '17 hours'
);
