--
-- PostgreSQL database dump
--

\restrict 7jh7pmeBDKM7C64E2k2uRb2ZhDZd8kkqa2HwekT6KLIeQUL7wmsQrssfrOqYp0m

-- Dumped from database version 16.13 (Debian 16.13-1.pgdg13+1)
-- Dumped by pg_dump version 16.13 (Debian 16.13-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.redaction_audit DROP CONSTRAINT IF EXISTS redaction_audit_report_id_fkey;
ALTER TABLE IF EXISTS ONLY public.intel_extracted DROP CONSTRAINT IF EXISTS intel_extracted_report_id_fkey;
ALTER TABLE IF EXISTS ONLY public.reports DROP CONSTRAINT IF EXISTS reports_pkey;
ALTER TABLE IF EXISTS ONLY public.redaction_audit DROP CONSTRAINT IF EXISTS redaction_audit_pkey;
ALTER TABLE IF EXISTS ONLY public.intel_extracted DROP CONSTRAINT IF EXISTS intel_extracted_pkey;
ALTER TABLE IF EXISTS public.redaction_audit ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.intel_extracted ALTER COLUMN id DROP DEFAULT;
DROP TABLE IF EXISTS public.reports;
DROP SEQUENCE IF EXISTS public.redaction_audit_id_seq;
DROP TABLE IF EXISTS public.redaction_audit;
DROP SEQUENCE IF EXISTS public.intel_extracted_id_seq;
DROP TABLE IF EXISTS public.intel_extracted;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: intel_extracted; Type: TABLE; Schema: public; Owner: edith_user
--

CREATE TABLE public.intel_extracted (
    id integer NOT NULL,
    report_id uuid,
    sector character varying(50),
    resource character varying(50),
    severity integer,
    event_type character varying(30),
    summary text,
    modifier_type character varying(30),
    modifier_value double precision,
    modifier_duration_hours integer,
    raw_llm_response jsonb,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT intel_extracted_severity_check CHECK (((severity >= 1) AND (severity <= 10)))
);


ALTER TABLE public.intel_extracted OWNER TO edith_user;

--
-- Name: intel_extracted_id_seq; Type: SEQUENCE; Schema: public; Owner: edith_user
--

CREATE SEQUENCE public.intel_extracted_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.intel_extracted_id_seq OWNER TO edith_user;

--
-- Name: intel_extracted_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: edith_user
--

ALTER SEQUENCE public.intel_extracted_id_seq OWNED BY public.intel_extracted.id;


--
-- Name: redaction_audit; Type: TABLE; Schema: public; Owner: edith_user
--

CREATE TABLE public.redaction_audit (
    id integer NOT NULL,
    report_id uuid,
    original_fragment text NOT NULL,
    replacement text NOT NULL,
    entity_type character varying(20),
    detection_layer character varying(20),
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.redaction_audit OWNER TO edith_user;

--
-- Name: redaction_audit_id_seq; Type: SEQUENCE; Schema: public; Owner: edith_user
--

CREATE SEQUENCE public.redaction_audit_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.redaction_audit_id_seq OWNER TO edith_user;

--
-- Name: redaction_audit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: edith_user
--

ALTER SEQUENCE public.redaction_audit_id_seq OWNED BY public.redaction_audit.id;


--
-- Name: reports; Type: TABLE; Schema: public; Owner: edith_user
--

CREATE TABLE public.reports (
    report_id uuid NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    operative_name text,
    operative_contact text,
    raw_text text NOT NULL,
    redacted_text text,
    priority character varying(30),
    status character varying(20) DEFAULT 'PENDING'::character varying,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.reports OWNER TO edith_user;

--
-- Name: intel_extracted id; Type: DEFAULT; Schema: public; Owner: edith_user
--

ALTER TABLE ONLY public.intel_extracted ALTER COLUMN id SET DEFAULT nextval('public.intel_extracted_id_seq'::regclass);


--
-- Name: redaction_audit id; Type: DEFAULT; Schema: public; Owner: edith_user
--

ALTER TABLE ONLY public.redaction_audit ALTER COLUMN id SET DEFAULT nextval('public.redaction_audit_id_seq'::regclass);


--
-- Data for Name: intel_extracted; Type: TABLE DATA; Schema: public; Owner: edith_user
--

COPY public.intel_extracted (id, report_id, sector, resource, severity, event_type, summary, modifier_type, modifier_value, modifier_duration_hours, raw_llm_response, created_at) FROM stdin;
\.


--
-- Data for Name: redaction_audit; Type: TABLE DATA; Schema: public; Owner: edith_user
--

COPY public.redaction_audit (id, report_id, original_fragment, replacement, entity_type, detection_layer, created_at) FROM stdin;
1	03d111aa-8ed1-4aa1-9264-0ae4abae8575	555-GOD-OF-THUNDER	[CONTACT-E563]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
2	03d111aa-8ed1-4aa1-9264-0ae4abae8575	Thor Odinson	[OPERATIVE-8320]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
3	5a1d7f22-54cf-45e6-b6f0-925e26d82d90	555-0199 (Black Widow Comms)	[CONTACT-1491]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
4	5a1d7f22-54cf-45e6-b6f0-925e26d82d90	Natasha Romanoff	[OPERATIVE-9671]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
5	81725b97-94f3-4237-ada2-c01a2b3da868	555-GOD-OF-THUNDER	[CONTACT-2C1D]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
6	81725b97-94f3-4237-ada2-c01a2b3da868	Thor Odinson	[OPERATIVE-9747]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
7	26e78ffe-ceda-4fbe-a8ac-1e890c20730f	555-GOD-OF-THUNDER	[CONTACT-88C7]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
8	26e78ffe-ceda-4fbe-a8ac-1e890c20730f	Thor Odinson	[OPERATIVE-4A1B]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
9	a475fdee-5628-4ea2-85a4-4180fa0f1ba8	555-0199 (Black Widow Comms)	[CONTACT-C913]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
10	a475fdee-5628-4ea2-85a4-4180fa0f1ba8	Natasha Romanoff	[OPERATIVE-96ED]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
11	62ed45cf-4da7-4859-88f3-b602cd71f6b3	555-0101 (Iron Line)	[CONTACT-1B47]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
12	62ed45cf-4da7-4859-88f3-b602cd71f6b3	Tony Stark	[OPERATIVE-2445]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
13	280f9f1f-f44d-4b8a-a475-ca243689c8bd	555-HULK-SMASH	[CONTACT-774F]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
14	280f9f1f-f44d-4b8a-a475-ca243689c8bd	Bruce Banner	[OPERATIVE-579D]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
15	e5e5e573-3554-4a00-9a91-d938387658ed	555-0199 (Black Widow Comms)	[CONTACT-A767]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
16	e5e5e573-3554-4a00-9a91-d938387658ed	Natasha Romanoff	[OPERATIVE-01E5]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
17	c0fdeadf-8e1c-456d-a08a-373d14b2565c	555-1941 (Shield Freq)	[CONTACT-369C]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
18	c0fdeadf-8e1c-456d-a08a-373d14b2565c	Steve Rogers	[OPERATIVE-FCD6]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
19	4f1ca0b2-ec9a-4849-b360-4af3f17453be	555-0101 (Iron Line)	[CONTACT-2F71]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
20	4f1ca0b2-ec9a-4849-b360-4af3f17453be	Tony Stark	[OPERATIVE-96CD]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
21	b9683c8d-c63d-4418-b66d-f87c5576b423	555-0101 (Iron Line)	[CONTACT-596C]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
22	b9683c8d-c63d-4418-b66d-f87c5576b423	Tony Stark	[OPERATIVE-7411]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
23	f8fa95f4-1398-4e85-9f10-d4e7afcabac4	555-GOD-OF-THUNDER	[CONTACT-69C4]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
24	f8fa95f4-1398-4e85-9f10-d4e7afcabac4	Thor Odinson	[OPERATIVE-C92C]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
25	7ec09765-a3fe-4078-a389-809dc12f7f8d	555-GOD-OF-THUNDER	[CONTACT-64E9]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
26	7ec09765-a3fe-4078-a389-809dc12f7f8d	Thor Odinson	[OPERATIVE-5035]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
27	9e4264b0-f801-4ac3-bd4d-1371d84ed2b0	555-0199 (Black Widow Comms)	[CONTACT-89BC]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
28	9e4264b0-f801-4ac3-bd4d-1371d84ed2b0	Natasha Romanoff	[OPERATIVE-1D94]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
29	2e577241-589a-4b66-8373-7e6b1d6e89c0	555-0101 (Iron Line)	[CONTACT-71AA]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
30	2e577241-589a-4b66-8373-7e6b1d6e89c0	Tony Stark	[OPERATIVE-6469]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
31	49abd305-c3d9-4523-aa4b-06b0bac59e31	555-1941 (Shield Freq)	[CONTACT-3511]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
32	49abd305-c3d9-4523-aa4b-06b0bac59e31	Steve Rogers	[OPERATIVE-FF2B]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
33	581980aa-5bd9-4187-8d9e-3715813e2963	555-0101 (Iron Line)	[CONTACT-DD67]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
34	581980aa-5bd9-4187-8d9e-3715813e2963	Tony Stark	[OPERATIVE-3E44]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
35	14e08f1c-88c0-47c3-8d98-4b9fa854f4e7	555-GOD-OF-THUNDER	[CONTACT-4343]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
36	14e08f1c-88c0-47c3-8d98-4b9fa854f4e7	Thor Odinson	[OPERATIVE-FEF8]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
37	54116893-0cc0-4261-800b-47f8a433deb7	555-0199 (Black Widow Comms)	[CONTACT-E43A]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
38	54116893-0cc0-4261-800b-47f8a433deb7	Natasha Romanoff	[OPERATIVE-1B5D]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
39	5f52297f-fed3-4a3e-9b49-be710ccf60c4	555-0199 (Black Widow Comms)	[CONTACT-F943]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
40	5f52297f-fed3-4a3e-9b49-be710ccf60c4	Natasha Romanoff	[OPERATIVE-E2AD]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
41	0073622f-676d-4abf-863e-c2b47f408e57	555-HULK-SMASH	[CONTACT-8ED0]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
42	0073622f-676d-4abf-863e-c2b47f408e57	Bruce Banner	[OPERATIVE-726C]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
43	2e3d3dc3-deb3-4521-84c7-7a2dfe269882	555-0101 (Iron Line)	[CONTACT-46CA]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
44	2e3d3dc3-deb3-4521-84c7-7a2dfe269882	Tony Stark	[OPERATIVE-3FE0]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
45	5726a129-76ec-482d-a602-d3aee819e427	555-0199 (Black Widow Comms)	[CONTACT-8F25]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
46	5726a129-76ec-482d-a602-d3aee819e427	Natasha Romanoff	[OPERATIVE-C5C7]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
47	5d06019e-dbd8-4da1-94b5-f74be9f5f5c1	555-0123 (Spider-Sense)	[CONTACT-FD21]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
48	5d06019e-dbd8-4da1-94b5-f74be9f5f5c1	Peter Parker	[OPERATIVE-26F7]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
49	dc83cf17-37e0-4805-97c1-8c86a8fba4dc	555-0101 (Iron Line)	[CONTACT-74E5]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
50	dc83cf17-37e0-4805-97c1-8c86a8fba4dc	Tony Stark	[OPERATIVE-DCA6]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
51	bbe81d1a-79c3-4156-a1c5-76f30cc15d7d	555-GOD-OF-THUNDER	[CONTACT-31F6]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
52	bbe81d1a-79c3-4156-a1c5-76f30cc15d7d	Thor Odinson	[OPERATIVE-D6B9]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
53	438856ae-cb9d-4d1e-ae13-88856f2d060c	555-HULK-SMASH	[CONTACT-1C35]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
54	438856ae-cb9d-4d1e-ae13-88856f2d060c	Bruce Banner	[OPERATIVE-E7A6]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
55	0be1e38e-0f5a-48cc-888b-9ad854995c21	555-HULK-SMASH	[CONTACT-DE78]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
56	0be1e38e-0f5a-48cc-888b-9ad854995c21	Bruce Banner	[OPERATIVE-C2D0]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
57	ad0ba7ba-5af1-4c87-8e15-f96523247478	555-GOD-OF-THUNDER	[CONTACT-D818]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
58	ad0ba7ba-5af1-4c87-8e15-f96523247478	Thor Odinson	[OPERATIVE-96B3]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
59	1ec710d7-f5e0-433c-867f-0c0a4fc95155	555-0101 (Iron Line)	[CONTACT-94BD]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
60	1ec710d7-f5e0-433c-867f-0c0a4fc95155	Tony Stark	[OPERATIVE-A85A]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
61	65f4838f-1eea-48e3-bb8c-0b6b741504ee	555-0123 (Spider-Sense)	[CONTACT-482F]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
62	65f4838f-1eea-48e3-bb8c-0b6b741504ee	Peter Parker	[OPERATIVE-4E98]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
63	df5c6b28-7317-44bd-8145-11b333a56254	555-0199 (Black Widow Comms)	[CONTACT-99AE]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
64	df5c6b28-7317-44bd-8145-11b333a56254	Natasha Romanoff	[OPERATIVE-B578]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
65	a2ca8dee-8c97-4cae-876b-d0c3120b67fa	555-0123 (Spider-Sense)	[CONTACT-8AA0]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
66	a2ca8dee-8c97-4cae-876b-d0c3120b67fa	Peter Parker	[OPERATIVE-5B3B]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
67	c6adce54-36db-4505-8a58-eab02fe9bc1f	555-GOD-OF-THUNDER	[CONTACT-E086]	PHONE	REGEX	2026-03-01 07:39:58.523473+00
68	c6adce54-36db-4505-8a58-eab02fe9bc1f	Thor Odinson	[OPERATIVE-EE8F]	PERSON	DICTIONARY	2026-03-01 07:39:58.523473+00
\.


--
-- Data for Name: reports; Type: TABLE DATA; Schema: public; Owner: edith_user
--

COPY public.reports (report_id, "timestamp", operative_name, operative_contact, raw_text, redacted_text, priority, status, created_at) FROM stdin;
a691a8b2-a957-492a-ae62-1b80016d6432	2026-01-15 21:41:48.828165+00	Tony Stark	555-0101 (Iron Line)	Urgent: Avengers Compound is critically low on Arc Reactor Cores. The civilians are worried.	Urgent: Avengers Compound is critically low on Arc Reactor Cores. The civilians are worried.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
5abfa4c0-7017-484d-a833-e9abe8637726	2026-01-16 08:35:48.828249+00	Natasha Romanoff	555-0199 (Black Widow Comms)	Heavy combat in Sanctum Sanctorum. Pym Particles supply chain is compromised. Need backup.	Heavy combat in Sanctum Sanctorum. Pym Particles supply chain is compromised. Need backup.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
8bc7bc93-cccc-46ee-b043-782df6c6d276	2026-01-15 20:30:48.828303+00	Thor Odinson	555-GOD-OF-THUNDER	The situation in Avengers Compound is dire. We need more Clean Water (L) or we lose the perimeter.	The situation in Avengers Compound is dire. We need more Clean Water (L) or we lose the perimeter.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
dc2e1068-1284-4999-95c1-7bb9be961fe2	2026-01-16 01:38:48.82857+00	Peter Parker	555-0123 (Spider-Sense)	Urgent: Avengers Compound is critically low on Medical Kits. The civilians are worried.	Urgent: Avengers Compound is critically low on Medical Kits. The civilians are worried.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
70f94524-35c3-4697-af4b-dd0156407fe4	2026-01-16 06:58:48.828669+00	Natasha Romanoff	555-0199 (Black Widow Comms)	Urgent: Wakanda is critically low on Vibranium (kg). The civilians are worried.	Urgent: Wakanda is critically low on Vibranium (kg). The civilians are worried.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
03d111aa-8ed1-4aa1-9264-0ae4abae8575	2026-01-16 02:21:48.828718+00	Thor Odinson	555-GOD-OF-THUNDER	Just a heads up, Sokovia is out of Vibranium (kg). This is Thor Odinson, call me back at 555-GOD-OF-THUNDER.	Just a heads up, Sokovia is out of Vibranium (kg). This is [OPERATIVE-8320], call me back at [CONTACT-E563].	High	REDACTED	2026-03-01 07:28:46.330359+00
97edcc21-8dbc-461a-b0d0-f52af1cd9f85	2026-01-15 18:08:48.828764+00	Bruce Banner	555-HULK-SMASH	Heavy combat in Sanctum Sanctorum. Pym Particles supply chain is compromised. Need backup.	Heavy combat in Sanctum Sanctorum. Pym Particles supply chain is compromised. Need backup.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
d09ec49c-83d8-4d20-b7b3-555a86bbe9e8	2026-01-15 20:31:48.828807+00	Thor Odinson	555-GOD-OF-THUNDER	Heavy combat in Avengers Compound. Medical Kits supply chain is compromised. Need backup.	Heavy combat in Avengers Compound. Medical Kits supply chain is compromised. Need backup.	High	REDACTED	2026-03-01 07:28:46.330359+00
52f93b2c-d2c5-42d4-b977-a3af4cc79f6f	2026-01-15 17:36:48.828863+00	Thor Odinson	555-GOD-OF-THUNDER	Heavy combat in Avengers Compound. Clean Water (L) supply chain is compromised. Need backup.	Heavy combat in Avengers Compound. Clean Water (L) supply chain is compromised. Need backup.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
a6d3d367-a743-4f6d-a276-09ebef398532	2026-01-16 05:26:48.828908+00	Thor Odinson	555-GOD-OF-THUNDER	The situation in Sokovia is dire. We need more Arc Reactor Cores or we lose the perimeter.	The situation in Sokovia is dire. We need more Arc Reactor Cores or we lose the perimeter.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
ee8540c7-5460-4809-b223-9e69dcf921fe	2026-01-15 21:05:48.828953+00	Bruce Banner	555-HULK-SMASH	Status update from Sanctum Sanctorum. We secured a cache of Arc Reactor Cores. Sending coordinates now.	Status update from Sanctum Sanctorum. We secured a cache of Arc Reactor Cores. Sending coordinates now.	High	REDACTED	2026-03-01 07:28:46.330359+00
b6bc0e94-3232-4818-9de8-1dfc918cc65f	2026-01-15 22:24:48.828998+00	Bruce Banner	555-HULK-SMASH	Urgent: Sanctum Sanctorum is critically low on Pym Particles. The civilians are worried.	Urgent: Sanctum Sanctorum is critically low on Pym Particles. The civilians are worried.	High	REDACTED	2026-03-01 07:28:46.330359+00
9d266b2f-a34f-4894-808e-58526ec03852	2026-01-15 22:19:48.829043+00	Thor Odinson	555-GOD-OF-THUNDER	Urgent: New Asgard is critically low on Clean Water (L). The civilians are worried.	Urgent: New Asgard is critically low on Clean Water (L). The civilians are worried.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
5a1d7f22-54cf-45e6-b6f0-925e26d82d90	2026-01-16 01:01:48.82909+00	Natasha Romanoff	555-0199 (Black Widow Comms)	Just a heads up, Avengers Compound is out of Pym Particles. This is Natasha Romanoff, call me back at 555-0199 (Black Widow Comms).	Just a heads up, Avengers Compound is out of Pym Particles. This is [OPERATIVE-9671], call me back at [CONTACT-1491].	High	REDACTED	2026-03-01 07:28:46.330359+00
fd2d3241-3cce-4d25-99f4-7118b24f971c	2026-01-16 08:16:48.829134+00	Bruce Banner	555-HULK-SMASH	Heavy combat in Sokovia. Vibranium (kg) supply chain is compromised. Need backup.	Heavy combat in Sokovia. Vibranium (kg) supply chain is compromised. Need backup.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
c5d079a5-15a7-4ae9-9545-9b9c93134fba	2026-01-16 02:18:48.829178+00	Steve Rogers	555-1941 (Shield Freq)	Urgent: New Asgard is critically low on Pym Particles. The civilians are worried.	Urgent: New Asgard is critically low on Pym Particles. The civilians are worried.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
4a14c58d-89d6-4d7a-906f-bf070ef4b6d8	2026-01-16 06:12:48.829221+00	Thor Odinson	555-GOD-OF-THUNDER	Urgent: Sanctum Sanctorum is critically low on Clean Water (L). The civilians are worried.	Urgent: Sanctum Sanctorum is critically low on Clean Water (L). The civilians are worried.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
81725b97-94f3-4237-ada2-c01a2b3da868	2026-01-15 20:35:48.829265+00	Thor Odinson	555-GOD-OF-THUNDER	Just a heads up, Sanctum Sanctorum is out of Clean Water (L). This is Thor Odinson, call me back at 555-GOD-OF-THUNDER.	Just a heads up, Sanctum Sanctorum is out of Clean Water (L). This is [OPERATIVE-9747], call me back at [CONTACT-2C1D].	High	REDACTED	2026-03-01 07:28:46.330359+00
af600588-84e8-4a78-8f6d-01d90eae85bc	2026-01-16 07:43:48.829309+00	Peter Parker	555-0123 (Spider-Sense)	Status update from Wakanda. We secured a cache of Clean Water (L). Sending coordinates now.	Status update from Wakanda. We secured a cache of Clean Water (L). Sending coordinates now.	High	REDACTED	2026-03-01 07:28:46.330359+00
26e78ffe-ceda-4fbe-a8ac-1e890c20730f	2026-01-15 16:28:48.829353+00	Thor Odinson	555-GOD-OF-THUNDER	Just a heads up, New Asgard is out of Clean Water (L). This is Thor Odinson, call me back at 555-GOD-OF-THUNDER.	Just a heads up, New Asgard is out of Clean Water (L). This is [OPERATIVE-4A1B], call me back at [CONTACT-88C7].	High	REDACTED	2026-03-01 07:28:46.330359+00
491a31ca-914c-4f8a-b82b-0d54ccf8efdf	2026-01-16 06:25:48.829396+00	Bruce Banner	555-HULK-SMASH	Status update from New Asgard. We secured a cache of Vibranium (kg). Sending coordinates now.	Status update from New Asgard. We secured a cache of Vibranium (kg). Sending coordinates now.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
5d2226e2-0c26-4628-95af-60cfde36e754	2026-01-15 22:43:48.82944+00	Thor Odinson	555-GOD-OF-THUNDER	Heavy combat in New Asgard. Pym Particles supply chain is compromised. Need backup.	Heavy combat in New Asgard. Pym Particles supply chain is compromised. Need backup.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
9218cb02-edd9-46ec-b1e3-dd0c74764933	2026-01-15 20:57:48.829484+00	Peter Parker	555-0123 (Spider-Sense)	Urgent: Sanctum Sanctorum is critically low on Arc Reactor Cores. The civilians are worried.	Urgent: Sanctum Sanctorum is critically low on Arc Reactor Cores. The civilians are worried.	High	REDACTED	2026-03-01 07:28:46.330359+00
83baba1c-ea03-4507-96a5-ca41ff6056ad	2026-01-16 04:11:48.829526+00	Thor Odinson	555-GOD-OF-THUNDER	Status update from Avengers Compound. We secured a cache of Clean Water (L). Sending coordinates now.	Status update from Avengers Compound. We secured a cache of Clean Water (L). Sending coordinates now.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
a475fdee-5628-4ea2-85a4-4180fa0f1ba8	2026-01-15 21:33:48.82957+00	Natasha Romanoff	555-0199 (Black Widow Comms)	Just a heads up, Wakanda is out of Vibranium (kg). This is Natasha Romanoff, call me back at 555-0199 (Black Widow Comms).	Just a heads up, Wakanda is out of Vibranium (kg). This is [OPERATIVE-96ED], call me back at [CONTACT-C913].	Routine	REDACTED	2026-03-01 07:28:46.330359+00
ee220c8e-6de2-4d20-ba67-a68e575ded02	2026-01-16 02:23:48.829614+00	Peter Parker	555-0123 (Spider-Sense)	The situation in Wakanda is dire. We need more Arc Reactor Cores or we lose the perimeter.	The situation in Wakanda is dire. We need more Arc Reactor Cores or we lose the perimeter.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
3fc705c4-de1b-49dd-bb32-8e682f2174fb	2026-01-15 22:38:48.829658+00	Tony Stark	555-0101 (Iron Line)	Heavy combat in New Asgard. Medical Kits supply chain is compromised. Need backup.	Heavy combat in New Asgard. Medical Kits supply chain is compromised. Need backup.	High	REDACTED	2026-03-01 07:28:46.330359+00
62ed45cf-4da7-4859-88f3-b602cd71f6b3	2026-01-16 00:02:48.829701+00	Tony Stark	555-0101 (Iron Line)	Just a heads up, New Asgard is out of Clean Water (L). This is Tony Stark, call me back at 555-0101 (Iron Line).	Just a heads up, New Asgard is out of Clean Water (L). This is [OPERATIVE-2445], call me back at [CONTACT-1B47].	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
46b6ccac-e55d-4c1c-be0c-e8c268ced42e	2026-01-16 01:45:48.829744+00	Tony Stark	555-0101 (Iron Line)	Status update from Wakanda. We secured a cache of Clean Water (L). Sending coordinates now.	Status update from Wakanda. We secured a cache of Clean Water (L). Sending coordinates now.	High	REDACTED	2026-03-01 07:28:46.330359+00
e7537f2c-f078-4279-b17b-61b31ccb1603	2026-01-16 00:27:48.829787+00	Peter Parker	555-0123 (Spider-Sense)	Status update from New Asgard. We secured a cache of Pym Particles. Sending coordinates now.	Status update from New Asgard. We secured a cache of Pym Particles. Sending coordinates now.	High	REDACTED	2026-03-01 07:28:46.330359+00
19ec5b4a-aeaa-4d98-b62c-95db50d5af4e	2026-01-15 22:28:48.829837+00	Tony Stark	555-0101 (Iron Line)	Heavy combat in Wakanda. Clean Water (L) supply chain is compromised. Need backup.	Heavy combat in Wakanda. Clean Water (L) supply chain is compromised. Need backup.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
38355c8e-b4cc-4f52-abc0-b416a004cf05	2026-01-16 03:33:48.829882+00	Bruce Banner	555-HULK-SMASH	The situation in Sanctum Sanctorum is dire. We need more Medical Kits or we lose the perimeter.	The situation in Sanctum Sanctorum is dire. We need more Medical Kits or we lose the perimeter.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
0cceaa3e-c6c1-4af7-bc81-a884d7e7d532	2026-01-16 07:30:48.829926+00	Thor Odinson	555-GOD-OF-THUNDER	Heavy combat in Sanctum Sanctorum. Pym Particles supply chain is compromised. Need backup.	Heavy combat in Sanctum Sanctorum. Pym Particles supply chain is compromised. Need backup.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
ead714f7-a7c7-4285-9924-cb57b145ec9f	2026-01-15 20:48:48.82997+00	Steve Rogers	555-1941 (Shield Freq)	Status update from Sokovia. We secured a cache of Clean Water (L). Sending coordinates now.	Status update from Sokovia. We secured a cache of Clean Water (L). Sending coordinates now.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
22f71be3-f16c-499d-a2d2-7cd02641bf82	2026-01-15 22:30:48.830012+00	Peter Parker	555-0123 (Spider-Sense)	The situation in Avengers Compound is dire. We need more Arc Reactor Cores or we lose the perimeter.	The situation in Avengers Compound is dire. We need more Arc Reactor Cores or we lose the perimeter.	High	REDACTED	2026-03-01 07:28:46.330359+00
53f37a33-b4e0-454b-b36a-4faac55fe86c	2026-01-16 02:15:48.830055+00	Peter Parker	555-0123 (Spider-Sense)	Urgent: Wakanda is critically low on Arc Reactor Cores. The civilians are worried.	Urgent: Wakanda is critically low on Arc Reactor Cores. The civilians are worried.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
44e328bd-5342-400e-b635-2193c5a73934	2026-01-15 20:40:48.830098+00	Peter Parker	555-0123 (Spider-Sense)	The situation in New Asgard is dire. We need more Arc Reactor Cores or we lose the perimeter.	The situation in New Asgard is dire. We need more Arc Reactor Cores or we lose the perimeter.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
48338415-f15a-4a3b-94cf-f0e58fa5e7ee	2026-01-16 00:38:48.83014+00	Steve Rogers	555-1941 (Shield Freq)	Status update from Sanctum Sanctorum. We secured a cache of Vibranium (kg). Sending coordinates now.	Status update from Sanctum Sanctorum. We secured a cache of Vibranium (kg). Sending coordinates now.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
ac3a7a84-452d-4c5f-85da-4b7c30bc54f1	2026-01-16 07:39:48.830182+00	Bruce Banner	555-HULK-SMASH	The situation in Wakanda is dire. We need more Pym Particles or we lose the perimeter.	The situation in Wakanda is dire. We need more Pym Particles or we lose the perimeter.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
280f9f1f-f44d-4b8a-a475-ca243689c8bd	2026-01-16 08:34:48.830225+00	Bruce Banner	555-HULK-SMASH	Just a heads up, New Asgard is out of Clean Water (L). This is Bruce Banner, call me back at 555-HULK-SMASH.	Just a heads up, New Asgard is out of Clean Water (L). This is [OPERATIVE-579D], call me back at [CONTACT-774F].	Routine	REDACTED	2026-03-01 07:28:46.330359+00
e5e5e573-3554-4a00-9a91-d938387658ed	2026-01-16 03:12:48.830268+00	Natasha Romanoff	555-0199 (Black Widow Comms)	Just a heads up, Avengers Compound is out of Vibranium (kg). This is Natasha Romanoff, call me back at 555-0199 (Black Widow Comms).	Just a heads up, Avengers Compound is out of Vibranium (kg). This is [OPERATIVE-01E5], call me back at [CONTACT-A767].	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
6fce8220-3f74-4e08-b026-c7b73dee226e	2026-01-15 16:38:48.83031+00	Thor Odinson	555-GOD-OF-THUNDER	Urgent: Wakanda is critically low on Clean Water (L). The civilians are worried.	Urgent: Wakanda is critically low on Clean Water (L). The civilians are worried.	High	REDACTED	2026-03-01 07:28:46.330359+00
b8a02d15-915a-4191-bd95-b4c0e8366e95	2026-01-16 02:53:48.830353+00	Steve Rogers	555-1941 (Shield Freq)	Urgent: New Asgard is critically low on Vibranium (kg). The civilians are worried.	Urgent: New Asgard is critically low on Vibranium (kg). The civilians are worried.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
3c90e5af-2176-4ddd-9f40-1a3ba9b7279f	2026-01-16 00:27:48.830395+00	Bruce Banner	555-HULK-SMASH	The situation in New Asgard is dire. We need more Vibranium (kg) or we lose the perimeter.	The situation in New Asgard is dire. We need more Vibranium (kg) or we lose the perimeter.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
bba1d7fc-9be1-4bd8-a83e-9d5363aaa535	2026-01-16 01:30:48.830438+00	Peter Parker	555-0123 (Spider-Sense)	The situation in Sanctum Sanctorum is dire. We need more Clean Water (L) or we lose the perimeter.	The situation in Sanctum Sanctorum is dire. We need more Clean Water (L) or we lose the perimeter.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
cb88326b-4bf8-4a56-8fae-741e9977bd09	2026-01-15 21:19:48.83048+00	Peter Parker	555-0123 (Spider-Sense)	Heavy combat in Avengers Compound. Arc Reactor Cores supply chain is compromised. Need backup.	Heavy combat in Avengers Compound. Arc Reactor Cores supply chain is compromised. Need backup.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
b10ce6bb-3e14-4bf9-8d67-41ca048d3bdc	2026-01-16 03:24:48.830522+00	Thor Odinson	555-GOD-OF-THUNDER	Status update from Wakanda. We secured a cache of Clean Water (L). Sending coordinates now.	Status update from Wakanda. We secured a cache of Clean Water (L). Sending coordinates now.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
f9c2f28e-15fc-4233-aa99-54979afde79d	2026-01-16 02:50:48.830564+00	Steve Rogers	555-1941 (Shield Freq)	Heavy combat in Sokovia. Medical Kits supply chain is compromised. Need backup.	Heavy combat in Sokovia. Medical Kits supply chain is compromised. Need backup.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
34169743-008c-442c-89c7-f93f604726ec	2026-01-15 22:51:48.830606+00	Bruce Banner	555-HULK-SMASH	Heavy combat in Avengers Compound. Pym Particles supply chain is compromised. Need backup.	Heavy combat in Avengers Compound. Pym Particles supply chain is compromised. Need backup.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
d950e86b-52fa-4ca1-9cab-3b8b1b3123e2	2026-01-15 19:33:48.830648+00	Tony Stark	555-0101 (Iron Line)	Urgent: New Asgard is critically low on Clean Water (L). The civilians are worried.	Urgent: New Asgard is critically low on Clean Water (L). The civilians are worried.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
9802091d-e1e8-4552-bef9-128f79327ac1	2026-01-16 08:30:48.830689+00	Peter Parker	555-0123 (Spider-Sense)	Urgent: Avengers Compound is critically low on Medical Kits. The civilians are worried.	Urgent: Avengers Compound is critically low on Medical Kits. The civilians are worried.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
8a913001-2f39-4d63-8e05-bbffc805c616	2026-01-15 17:12:48.830731+00	Steve Rogers	555-1941 (Shield Freq)	Status update from New Asgard. We secured a cache of Vibranium (kg). Sending coordinates now.	Status update from New Asgard. We secured a cache of Vibranium (kg). Sending coordinates now.	High	REDACTED	2026-03-01 07:28:46.330359+00
0e9b69d9-860c-45df-8645-dd5c8d1142f2	2026-01-16 02:03:48.830773+00	Thor Odinson	555-GOD-OF-THUNDER	The situation in Sokovia is dire. We need more Medical Kits or we lose the perimeter.	The situation in Sokovia is dire. We need more Medical Kits or we lose the perimeter.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
1478e7a6-d607-4b2c-ab28-dc8e1d00b3d9	2026-01-16 05:12:48.830817+00	Tony Stark	555-0101 (Iron Line)	Heavy combat in Sanctum Sanctorum. Clean Water (L) supply chain is compromised. Need backup.	Heavy combat in Sanctum Sanctorum. Clean Water (L) supply chain is compromised. Need backup.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
9ff2b82f-10a3-49b3-9b3b-4ac0ee21a1c0	2026-01-16 00:44:48.830868+00	Natasha Romanoff	555-0199 (Black Widow Comms)	Status update from Wakanda. We secured a cache of Pym Particles. Sending coordinates now.	Status update from Wakanda. We secured a cache of Pym Particles. Sending coordinates now.	High	REDACTED	2026-03-01 07:28:46.330359+00
c0fdeadf-8e1c-456d-a08a-373d14b2565c	2026-01-15 20:21:48.830912+00	Steve Rogers	555-1941 (Shield Freq)	Just a heads up, Sokovia is out of Clean Water (L). This is Steve Rogers, call me back at 555-1941 (Shield Freq).	Just a heads up, Sokovia is out of Clean Water (L). This is [OPERATIVE-FCD6], call me back at [CONTACT-369C].	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
258a7b13-c8a1-41f6-9f62-a54cb7947564	2026-01-15 22:15:48.830954+00	Peter Parker	555-0123 (Spider-Sense)	Heavy combat in New Asgard. Clean Water (L) supply chain is compromised. Need backup.	Heavy combat in New Asgard. Clean Water (L) supply chain is compromised. Need backup.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
4f1ca0b2-ec9a-4849-b360-4af3f17453be	2026-01-15 17:55:48.830999+00	Tony Stark	555-0101 (Iron Line)	Just a heads up, Sanctum Sanctorum is out of Arc Reactor Cores. This is Tony Stark, call me back at 555-0101 (Iron Line).	Just a heads up, Sanctum Sanctorum is out of Arc Reactor Cores. This is [OPERATIVE-96CD], call me back at [CONTACT-2F71].	High	REDACTED	2026-03-01 07:28:46.330359+00
82203d6e-61df-478a-8b5c-30867aeb624f	2026-01-16 05:26:48.831042+00	Tony Stark	555-0101 (Iron Line)	Urgent: Sokovia is critically low on Arc Reactor Cores. The civilians are worried.	Urgent: Sokovia is critically low on Arc Reactor Cores. The civilians are worried.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
1f97bd89-af6e-458b-bdf2-44f95cef86a8	2026-01-16 06:23:48.831094+00	Thor Odinson	555-GOD-OF-THUNDER	Urgent: Sokovia is critically low on Pym Particles. The civilians are worried.	Urgent: Sokovia is critically low on Pym Particles. The civilians are worried.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
3ed6d2d3-a916-411b-ba8b-4d09e207aa63	2026-01-16 08:51:48.831152+00	Peter Parker	555-0123 (Spider-Sense)	Urgent: Wakanda is critically low on Pym Particles. The civilians are worried.	Urgent: Wakanda is critically low on Pym Particles. The civilians are worried.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
2e5d9050-3df6-4b95-ba55-55380ea9256c	2026-01-16 06:20:48.831196+00	Steve Rogers	555-1941 (Shield Freq)	Urgent: New Asgard is critically low on Vibranium (kg). The civilians are worried.	Urgent: New Asgard is critically low on Vibranium (kg). The civilians are worried.	High	REDACTED	2026-03-01 07:28:46.330359+00
ba720c0a-c59e-4522-81cf-c55c75b143f9	2026-01-16 04:55:48.83124+00	Bruce Banner	555-HULK-SMASH	The situation in Sanctum Sanctorum is dire. We need more Pym Particles or we lose the perimeter.	The situation in Sanctum Sanctorum is dire. We need more Pym Particles or we lose the perimeter.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
32225593-bfcc-480a-bfe1-3c65799446f3	2026-01-16 08:45:48.831282+00	Natasha Romanoff	555-0199 (Black Widow Comms)	The situation in Avengers Compound is dire. We need more Pym Particles or we lose the perimeter.	The situation in Avengers Compound is dire. We need more Pym Particles or we lose the perimeter.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
932849e3-fce9-4f0b-a7a1-d87e3954836f	2026-01-15 20:40:48.831325+00	Tony Stark	555-0101 (Iron Line)	Heavy combat in Sokovia. Medical Kits supply chain is compromised. Need backup.	Heavy combat in Sokovia. Medical Kits supply chain is compromised. Need backup.	High	REDACTED	2026-03-01 07:28:46.330359+00
ad687cab-bc76-47a7-8aa1-38393144cef1	2026-01-16 07:57:48.831368+00	Thor Odinson	555-GOD-OF-THUNDER	Heavy combat in New Asgard. Medical Kits supply chain is compromised. Need backup.	Heavy combat in New Asgard. Medical Kits supply chain is compromised. Need backup.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
ba64f2be-9f85-4d4d-810d-01c86e550955	2026-01-15 23:21:48.83141+00	Bruce Banner	555-HULK-SMASH	Urgent: Sanctum Sanctorum is critically low on Pym Particles. The civilians are worried.	Urgent: Sanctum Sanctorum is critically low on Pym Particles. The civilians are worried.	High	REDACTED	2026-03-01 07:28:46.330359+00
83166138-95ec-4fe2-9a80-069a3666549d	2026-01-16 04:39:48.831452+00	Thor Odinson	555-GOD-OF-THUNDER	The situation in Sanctum Sanctorum is dire. We need more Pym Particles or we lose the perimeter.	The situation in Sanctum Sanctorum is dire. We need more Pym Particles or we lose the perimeter.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
9b7476f8-7853-4479-a0e3-2c5502eb7219	2026-01-16 08:27:48.831494+00	Thor Odinson	555-GOD-OF-THUNDER	Heavy combat in Wakanda. Medical Kits supply chain is compromised. Need backup.	Heavy combat in Wakanda. Medical Kits supply chain is compromised. Need backup.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
b9683c8d-c63d-4418-b66d-f87c5576b423	2026-01-16 06:11:48.831536+00	Tony Stark	555-0101 (Iron Line)	Just a heads up, Sanctum Sanctorum is out of Pym Particles. This is Tony Stark, call me back at 555-0101 (Iron Line).	Just a heads up, Sanctum Sanctorum is out of Pym Particles. This is [OPERATIVE-7411], call me back at [CONTACT-596C].	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
3cc030ff-03e5-475d-bef0-8cb3e4d69e7a	2026-01-16 03:55:48.831579+00	Tony Stark	555-0101 (Iron Line)	The situation in Sokovia is dire. We need more Pym Particles or we lose the perimeter.	The situation in Sokovia is dire. We need more Pym Particles or we lose the perimeter.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
3d8adac3-9eee-4ab5-82a5-e4ee08507e73	2026-01-16 03:25:48.831621+00	Tony Stark	555-0101 (Iron Line)	Urgent: Sanctum Sanctorum is critically low on Arc Reactor Cores. The civilians are worried.	Urgent: Sanctum Sanctorum is critically low on Arc Reactor Cores. The civilians are worried.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
bd72abe1-b7b4-4b9b-b361-6434830d65bd	2026-01-16 07:35:48.831665+00	Natasha Romanoff	555-0199 (Black Widow Comms)	Status update from Avengers Compound. We secured a cache of Clean Water (L). Sending coordinates now.	Status update from Avengers Compound. We secured a cache of Clean Water (L). Sending coordinates now.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
c1ce8d48-a7ee-4122-942a-4f793b7b8af7	2026-01-15 23:51:48.831714+00	Tony Stark	555-0101 (Iron Line)	The situation in Wakanda is dire. We need more Vibranium (kg) or we lose the perimeter.	The situation in Wakanda is dire. We need more Vibranium (kg) or we lose the perimeter.	High	REDACTED	2026-03-01 07:28:46.330359+00
7d0697c2-dd1d-404b-b3c9-144bc38a292c	2026-01-15 23:12:48.831759+00	Steve Rogers	555-1941 (Shield Freq)	Status update from Wakanda. We secured a cache of Medical Kits. Sending coordinates now.	Status update from Wakanda. We secured a cache of Medical Kits. Sending coordinates now.	High	REDACTED	2026-03-01 07:28:46.330359+00
f8fa95f4-1398-4e85-9f10-d4e7afcabac4	2026-01-15 20:47:48.831802+00	Thor Odinson	555-GOD-OF-THUNDER	Just a heads up, Sanctum Sanctorum is out of Clean Water (L). This is Thor Odinson, call me back at 555-GOD-OF-THUNDER.	Just a heads up, Sanctum Sanctorum is out of Clean Water (L). This is [OPERATIVE-C92C], call me back at [CONTACT-69C4].	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
7ec09765-a3fe-4078-a389-809dc12f7f8d	2026-01-15 18:00:48.832019+00	Thor Odinson	555-GOD-OF-THUNDER	Just a heads up, Avengers Compound is out of Medical Kits. This is Thor Odinson, call me back at 555-GOD-OF-THUNDER.	Just a heads up, Avengers Compound is out of Medical Kits. This is [OPERATIVE-5035], call me back at [CONTACT-64E9].	High	REDACTED	2026-03-01 07:28:46.330359+00
5058c909-a4a6-479e-bea8-d3f2d2263e61	2026-01-15 20:04:48.832075+00	Tony Stark	555-0101 (Iron Line)	Status update from Avengers Compound. We secured a cache of Medical Kits. Sending coordinates now.	Status update from Avengers Compound. We secured a cache of Medical Kits. Sending coordinates now.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
7e9ba599-0752-4c08-9913-b692c86790b5	2026-01-15 23:13:48.832119+00	Steve Rogers	555-1941 (Shield Freq)	Status update from Sanctum Sanctorum. We secured a cache of Pym Particles. Sending coordinates now.	Status update from Sanctum Sanctorum. We secured a cache of Pym Particles. Sending coordinates now.	High	REDACTED	2026-03-01 07:28:46.330359+00
9e4264b0-f801-4ac3-bd4d-1371d84ed2b0	2026-01-15 23:27:48.832163+00	Natasha Romanoff	555-0199 (Black Widow Comms)	Just a heads up, Avengers Compound is out of Clean Water (L). This is Natasha Romanoff, call me back at 555-0199 (Black Widow Comms).	Just a heads up, Avengers Compound is out of Clean Water (L). This is [OPERATIVE-1D94], call me back at [CONTACT-89BC].	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
68809354-3a6e-4c60-a3b3-e4285b11a6b6	2026-01-16 02:05:48.832208+00	Peter Parker	555-0123 (Spider-Sense)	The situation in Wakanda is dire. We need more Clean Water (L) or we lose the perimeter.	The situation in Wakanda is dire. We need more Clean Water (L) or we lose the perimeter.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
7c9fafca-d618-44a1-b9bb-a36eb278aa34	2026-01-16 05:43:48.832253+00	Thor Odinson	555-GOD-OF-THUNDER	Urgent: Wakanda is critically low on Arc Reactor Cores. The civilians are worried.	Urgent: Wakanda is critically low on Arc Reactor Cores. The civilians are worried.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
7e500f25-5bd8-4c7b-aa36-084832f52e52	2026-01-15 16:58:48.8323+00	Bruce Banner	555-HULK-SMASH	The situation in New Asgard is dire. We need more Clean Water (L) or we lose the perimeter.	The situation in New Asgard is dire. We need more Clean Water (L) or we lose the perimeter.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
c7cf339b-0036-47a6-9ccd-0f54bbc0f46d	2026-01-15 21:09:48.832342+00	Steve Rogers	555-1941 (Shield Freq)	Status update from Avengers Compound. We secured a cache of Pym Particles. Sending coordinates now.	Status update from Avengers Compound. We secured a cache of Pym Particles. Sending coordinates now.	High	REDACTED	2026-03-01 07:28:46.330359+00
7abd575d-c657-4756-8989-1461e1d3ba18	2026-01-16 00:04:48.832384+00	Natasha Romanoff	555-0199 (Black Widow Comms)	Urgent: New Asgard is critically low on Pym Particles. The civilians are worried.	Urgent: New Asgard is critically low on Pym Particles. The civilians are worried.	High	REDACTED	2026-03-01 07:28:46.330359+00
2d5e5b01-ad0f-4527-b6f5-5e24ab59457c	2026-01-16 01:39:48.832426+00	Natasha Romanoff	555-0199 (Black Widow Comms)	The situation in Avengers Compound is dire. We need more Vibranium (kg) or we lose the perimeter.	The situation in Avengers Compound is dire. We need more Vibranium (kg) or we lose the perimeter.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
6ab72e85-5463-49b6-99da-5a7b3be34753	2026-01-15 20:36:48.832468+00	Steve Rogers	555-1941 (Shield Freq)	Urgent: Sokovia is critically low on Clean Water (L). The civilians are worried.	Urgent: Sokovia is critically low on Clean Water (L). The civilians are worried.	High	REDACTED	2026-03-01 07:28:46.330359+00
6f062fce-1dba-4fcf-8925-a367bad41930	2026-01-16 07:27:48.832511+00	Peter Parker	555-0123 (Spider-Sense)	Status update from New Asgard. We secured a cache of Medical Kits. Sending coordinates now.	Status update from New Asgard. We secured a cache of Medical Kits. Sending coordinates now.	High	REDACTED	2026-03-01 07:28:46.330359+00
7f371910-6015-4516-a34c-657bec04c13b	2026-01-15 22:39:48.832554+00	Natasha Romanoff	555-0199 (Black Widow Comms)	The situation in Wakanda is dire. We need more Vibranium (kg) or we lose the perimeter.	The situation in Wakanda is dire. We need more Vibranium (kg) or we lose the perimeter.	High	REDACTED	2026-03-01 07:28:46.330359+00
cc3384fa-ee58-490f-9fd2-1a38bc4c090f	2026-01-15 22:03:48.832597+00	Natasha Romanoff	555-0199 (Black Widow Comms)	Heavy combat in Sanctum Sanctorum. Vibranium (kg) supply chain is compromised. Need backup.	Heavy combat in Sanctum Sanctorum. Vibranium (kg) supply chain is compromised. Need backup.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
2e577241-589a-4b66-8373-7e6b1d6e89c0	2026-01-16 06:59:48.83264+00	Tony Stark	555-0101 (Iron Line)	Just a heads up, Sanctum Sanctorum is out of Vibranium (kg). This is Tony Stark, call me back at 555-0101 (Iron Line).	Just a heads up, Sanctum Sanctorum is out of Vibranium (kg). This is [OPERATIVE-6469], call me back at [CONTACT-71AA].	Routine	REDACTED	2026-03-01 07:28:46.330359+00
f11fb7b9-e893-42f7-98be-f2d2f74d5852	2026-01-16 02:04:48.832682+00	Steve Rogers	555-1941 (Shield Freq)	Status update from Sokovia. We secured a cache of Arc Reactor Cores. Sending coordinates now.	Status update from Sokovia. We secured a cache of Arc Reactor Cores. Sending coordinates now.	High	REDACTED	2026-03-01 07:28:46.330359+00
2c2e66cd-437d-4fb8-bb81-a63f07be178a	2026-01-15 19:59:48.832724+00	Bruce Banner	555-HULK-SMASH	Heavy combat in Sokovia. Medical Kits supply chain is compromised. Need backup.	Heavy combat in Sokovia. Medical Kits supply chain is compromised. Need backup.	High	REDACTED	2026-03-01 07:28:46.330359+00
dc8085b9-89d2-4d49-8d0b-9e1c2e47d79b	2026-01-15 17:12:48.832767+00	Peter Parker	555-0123 (Spider-Sense)	Status update from Wakanda. We secured a cache of Medical Kits. Sending coordinates now.	Status update from Wakanda. We secured a cache of Medical Kits. Sending coordinates now.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
2015fd9d-7c3d-4a09-9af1-91a8348837d4	2026-01-15 16:44:48.832809+00	Natasha Romanoff	555-0199 (Black Widow Comms)	Urgent: New Asgard is critically low on Medical Kits. The civilians are worried.	Urgent: New Asgard is critically low on Medical Kits. The civilians are worried.	High	REDACTED	2026-03-01 07:28:46.330359+00
e423cef4-4feb-4b85-a2f5-9e7f9ef48c4c	2026-01-15 23:28:48.832863+00	Tony Stark	555-0101 (Iron Line)	Urgent: New Asgard is critically low on Arc Reactor Cores. The civilians are worried.	Urgent: New Asgard is critically low on Arc Reactor Cores. The civilians are worried.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
c97ebf96-b510-46e5-8058-74a0356b6ec3	2026-01-16 06:14:48.832907+00	Steve Rogers	555-1941 (Shield Freq)	Heavy combat in Sanctum Sanctorum. Medical Kits supply chain is compromised. Need backup.	Heavy combat in Sanctum Sanctorum. Medical Kits supply chain is compromised. Need backup.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
08bb6d4e-77b3-4f86-a983-a8ede912e05c	2026-01-16 05:18:48.83295+00	Steve Rogers	555-1941 (Shield Freq)	The situation in Sokovia is dire. We need more Pym Particles or we lose the perimeter.	The situation in Sokovia is dire. We need more Pym Particles or we lose the perimeter.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
9f3c07c1-b09f-44bc-9bc1-3fec21b8cfec	2026-01-16 05:35:48.832994+00	Thor Odinson	555-GOD-OF-THUNDER	Heavy combat in Wakanda. Vibranium (kg) supply chain is compromised. Need backup.	Heavy combat in Wakanda. Vibranium (kg) supply chain is compromised. Need backup.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
8058feb4-ca3a-4a67-9d42-818da487ecd4	2026-01-15 21:00:48.833036+00	Natasha Romanoff	555-0199 (Black Widow Comms)	Heavy combat in Sanctum Sanctorum. Pym Particles supply chain is compromised. Need backup.	Heavy combat in Sanctum Sanctorum. Pym Particles supply chain is compromised. Need backup.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
f4279e6b-472f-4be0-8c37-7778fec5186b	2026-01-16 04:40:48.833079+00	Thor Odinson	555-GOD-OF-THUNDER	Urgent: Sanctum Sanctorum is critically low on Arc Reactor Cores. The civilians are worried.	Urgent: Sanctum Sanctorum is critically low on Arc Reactor Cores. The civilians are worried.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
e7ab8868-3483-4f03-a990-3697c2fd74d8	2026-01-16 06:21:48.833122+00	Thor Odinson	555-GOD-OF-THUNDER	Heavy combat in Sokovia. Pym Particles supply chain is compromised. Need backup.	Heavy combat in Sokovia. Pym Particles supply chain is compromised. Need backup.	High	REDACTED	2026-03-01 07:28:46.330359+00
ce08b404-01e0-429f-b3fe-bed78b9c0c1d	2026-01-16 03:55:48.833164+00	Bruce Banner	555-HULK-SMASH	Urgent: Sanctum Sanctorum is critically low on Clean Water (L). The civilians are worried.	Urgent: Sanctum Sanctorum is critically low on Clean Water (L). The civilians are worried.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
1c296d8f-3b6c-4456-ba7f-241b453fcd97	2026-01-16 04:53:48.833207+00	Thor Odinson	555-GOD-OF-THUNDER	Status update from Sokovia. We secured a cache of Medical Kits. Sending coordinates now.	Status update from Sokovia. We secured a cache of Medical Kits. Sending coordinates now.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
30156d14-d317-49f5-bfd0-0d2fef1023ad	2026-01-15 19:21:48.83325+00	Bruce Banner	555-HULK-SMASH	Status update from Sokovia. We secured a cache of Vibranium (kg). Sending coordinates now.	Status update from Sokovia. We secured a cache of Vibranium (kg). Sending coordinates now.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
e1e4f3cd-89f7-41a4-8924-ccfad2f4e024	2026-01-15 20:55:48.833292+00	Peter Parker	555-0123 (Spider-Sense)	Status update from Wakanda. We secured a cache of Vibranium (kg). Sending coordinates now.	Status update from Wakanda. We secured a cache of Vibranium (kg). Sending coordinates now.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
546af60c-58de-4cc1-a6f9-da5789659c89	2026-01-15 20:23:48.833334+00	Thor Odinson	555-GOD-OF-THUNDER	Urgent: Avengers Compound is critically low on Clean Water (L). The civilians are worried.	Urgent: Avengers Compound is critically low on Clean Water (L). The civilians are worried.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
5d33e692-447e-4f14-a43b-d9bed6161804	2026-01-16 02:29:48.833376+00	Steve Rogers	555-1941 (Shield Freq)	Heavy combat in Wakanda. Vibranium (kg) supply chain is compromised. Need backup.	Heavy combat in Wakanda. Vibranium (kg) supply chain is compromised. Need backup.	High	REDACTED	2026-03-01 07:28:46.330359+00
fb401b87-d913-4a92-be96-a61c4dc3d223	2026-01-15 17:08:48.833418+00	Natasha Romanoff	555-0199 (Black Widow Comms)	Urgent: Wakanda is critically low on Vibranium (kg). The civilians are worried.	Urgent: Wakanda is critically low on Vibranium (kg). The civilians are worried.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
7afdcc19-ba57-48c5-ac75-f2338df76a11	2026-01-15 19:21:48.833461+00	Steve Rogers	555-1941 (Shield Freq)	Urgent: Sokovia is critically low on Clean Water (L). The civilians are worried.	Urgent: Sokovia is critically low on Clean Water (L). The civilians are worried.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
785f9683-d895-4f02-ae4d-58c288841d7c	2026-01-15 16:28:48.833503+00	Bruce Banner	555-HULK-SMASH	The situation in Sanctum Sanctorum is dire. We need more Arc Reactor Cores or we lose the perimeter.	The situation in Sanctum Sanctorum is dire. We need more Arc Reactor Cores or we lose the perimeter.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
72476e4b-451b-4296-9a52-4cb03e157baf	2026-01-16 04:48:48.833545+00	Thor Odinson	555-GOD-OF-THUNDER	Urgent: Avengers Compound is critically low on Clean Water (L). The civilians are worried.	Urgent: Avengers Compound is critically low on Clean Water (L). The civilians are worried.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
49abd305-c3d9-4523-aa4b-06b0bac59e31	2026-01-16 06:24:48.833589+00	Steve Rogers	555-1941 (Shield Freq)	Just a heads up, Sokovia is out of Clean Water (L). This is Steve Rogers, call me back at 555-1941 (Shield Freq).	Just a heads up, Sokovia is out of Clean Water (L). This is [OPERATIVE-FF2B], call me back at [CONTACT-3511].	Routine	REDACTED	2026-03-01 07:28:46.330359+00
b059ba1e-3681-4c83-b97d-a2563858b2dc	2026-01-16 00:18:48.833631+00	Steve Rogers	555-1941 (Shield Freq)	Heavy combat in Sanctum Sanctorum. Arc Reactor Cores supply chain is compromised. Need backup.	Heavy combat in Sanctum Sanctorum. Arc Reactor Cores supply chain is compromised. Need backup.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
03552f24-8105-4aa7-be40-e7e9eab991fa	2026-01-16 05:29:48.833673+00	Bruce Banner	555-HULK-SMASH	Urgent: Sanctum Sanctorum is critically low on Medical Kits. The civilians are worried.	Urgent: Sanctum Sanctorum is critically low on Medical Kits. The civilians are worried.	High	REDACTED	2026-03-01 07:28:46.330359+00
e94cd6d5-3988-4bba-9d12-3b38358b07d9	2026-01-16 03:38:48.833715+00	Peter Parker	555-0123 (Spider-Sense)	The situation in New Asgard is dire. We need more Pym Particles or we lose the perimeter.	The situation in New Asgard is dire. We need more Pym Particles or we lose the perimeter.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
05dbac73-8e9b-4ee3-8efa-e19b934c6ed7	2026-01-15 20:48:48.833757+00	Tony Stark	555-0101 (Iron Line)	The situation in Avengers Compound is dire. We need more Clean Water (L) or we lose the perimeter.	The situation in Avengers Compound is dire. We need more Clean Water (L) or we lose the perimeter.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
d5e898a0-a827-4969-a258-3ecdeabed4fd	2026-01-16 03:42:48.833799+00	Peter Parker	555-0123 (Spider-Sense)	Urgent: Sanctum Sanctorum is critically low on Clean Water (L). The civilians are worried.	Urgent: Sanctum Sanctorum is critically low on Clean Water (L). The civilians are worried.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
2ce9ed12-2b1e-479d-9578-82a363ae4467	2026-01-15 22:54:48.833856+00	Thor Odinson	555-GOD-OF-THUNDER	Status update from Sokovia. We secured a cache of Arc Reactor Cores. Sending coordinates now.	Status update from Sokovia. We secured a cache of Arc Reactor Cores. Sending coordinates now.	High	REDACTED	2026-03-01 07:28:46.330359+00
9a2ebb23-e4fa-4cb3-b9b1-f5dd4b57f67d	2026-01-15 18:58:48.833907+00	Peter Parker	555-0123 (Spider-Sense)	The situation in Sanctum Sanctorum is dire. We need more Medical Kits or we lose the perimeter.	The situation in Sanctum Sanctorum is dire. We need more Medical Kits or we lose the perimeter.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
581980aa-5bd9-4187-8d9e-3715813e2963	2026-01-15 20:50:48.833961+00	Tony Stark	555-0101 (Iron Line)	Just a heads up, Sokovia is out of Medical Kits. This is Tony Stark, call me back at 555-0101 (Iron Line).	Just a heads up, Sokovia is out of Medical Kits. This is [OPERATIVE-3E44], call me back at [CONTACT-DD67].	Routine	REDACTED	2026-03-01 07:28:46.330359+00
013a5ed1-375b-4164-ab10-369fe7c27874	2026-01-16 08:07:48.834005+00	Steve Rogers	555-1941 (Shield Freq)	Urgent: Sokovia is critically low on Clean Water (L). The civilians are worried.	Urgent: Sokovia is critically low on Clean Water (L). The civilians are worried.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
1a167395-0f3b-4cc0-8ce0-0e797b06cf46	2026-01-15 23:43:48.834048+00	Thor Odinson	555-GOD-OF-THUNDER	Status update from Sanctum Sanctorum. We secured a cache of Clean Water (L). Sending coordinates now.	Status update from Sanctum Sanctorum. We secured a cache of Clean Water (L). Sending coordinates now.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
14e08f1c-88c0-47c3-8d98-4b9fa854f4e7	2026-01-16 08:25:48.83409+00	Thor Odinson	555-GOD-OF-THUNDER	Just a heads up, Wakanda is out of Arc Reactor Cores. This is Thor Odinson, call me back at 555-GOD-OF-THUNDER.	Just a heads up, Wakanda is out of Arc Reactor Cores. This is [OPERATIVE-FEF8], call me back at [CONTACT-4343].	Routine	REDACTED	2026-03-01 07:28:46.330359+00
54116893-0cc0-4261-800b-47f8a433deb7	2026-01-15 21:14:48.834133+00	Natasha Romanoff	555-0199 (Black Widow Comms)	Just a heads up, Sanctum Sanctorum is out of Medical Kits. This is Natasha Romanoff, call me back at 555-0199 (Black Widow Comms).	Just a heads up, Sanctum Sanctorum is out of Medical Kits. This is [OPERATIVE-1B5D], call me back at [CONTACT-E43A].	Routine	REDACTED	2026-03-01 07:28:46.330359+00
6ba33eee-0a60-4c28-a4be-3f913a59c787	2026-01-16 08:29:48.834175+00	Tony Stark	555-0101 (Iron Line)	Status update from Sanctum Sanctorum. We secured a cache of Medical Kits. Sending coordinates now.	Status update from Sanctum Sanctorum. We secured a cache of Medical Kits. Sending coordinates now.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
7fe68a85-339c-4b4a-a19c-ccdfba69d584	2026-01-16 07:35:48.834218+00	Thor Odinson	555-GOD-OF-THUNDER	The situation in Avengers Compound is dire. We need more Vibranium (kg) or we lose the perimeter.	The situation in Avengers Compound is dire. We need more Vibranium (kg) or we lose the perimeter.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
039ae048-7a18-41f1-8af7-8c05dc415db5	2026-01-15 21:22:48.83426+00	Natasha Romanoff	555-0199 (Black Widow Comms)	Urgent: Wakanda is critically low on Clean Water (L). The civilians are worried.	Urgent: Wakanda is critically low on Clean Water (L). The civilians are worried.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
8396dad2-466c-46a7-85c7-fb8a71538cc0	2026-01-15 23:50:48.834302+00	Thor Odinson	555-GOD-OF-THUNDER	Urgent: Sanctum Sanctorum is critically low on Clean Water (L). The civilians are worried.	Urgent: Sanctum Sanctorum is critically low on Clean Water (L). The civilians are worried.	High	REDACTED	2026-03-01 07:28:46.330359+00
3e34c4ac-b075-4173-9883-3f3ad94711b4	2026-01-16 08:32:48.834345+00	Thor Odinson	555-GOD-OF-THUNDER	Heavy combat in Sanctum Sanctorum. Pym Particles supply chain is compromised. Need backup.	Heavy combat in Sanctum Sanctorum. Pym Particles supply chain is compromised. Need backup.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
9bf6f6fb-2a6b-4605-ae78-8d82c9fe126a	2026-01-16 07:59:48.834388+00	Tony Stark	555-0101 (Iron Line)	Heavy combat in Avengers Compound. Pym Particles supply chain is compromised. Need backup.	Heavy combat in Avengers Compound. Pym Particles supply chain is compromised. Need backup.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
e9475ca4-b892-489f-b721-b25bf7320459	2026-01-16 01:41:48.83443+00	Tony Stark	555-0101 (Iron Line)	Urgent: Avengers Compound is critically low on Medical Kits. The civilians are worried.	Urgent: Avengers Compound is critically low on Medical Kits. The civilians are worried.	High	REDACTED	2026-03-01 07:28:46.330359+00
a4bde49a-3e58-40ce-8bbc-29a592947760	2026-01-15 18:34:48.834472+00	Natasha Romanoff	555-0199 (Black Widow Comms)	Status update from Sanctum Sanctorum. We secured a cache of Vibranium (kg). Sending coordinates now.	Status update from Sanctum Sanctorum. We secured a cache of Vibranium (kg). Sending coordinates now.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
0a3c6ed8-d555-4c55-a955-84fed324c549	2026-01-16 07:53:48.834514+00	Bruce Banner	555-HULK-SMASH	Status update from New Asgard. We secured a cache of Pym Particles. Sending coordinates now.	Status update from New Asgard. We secured a cache of Pym Particles. Sending coordinates now.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
4905d978-d525-4e70-9810-88d21973522d	2026-01-15 18:57:48.834556+00	Bruce Banner	555-HULK-SMASH	Status update from Sokovia. We secured a cache of Pym Particles. Sending coordinates now.	Status update from Sokovia. We secured a cache of Pym Particles. Sending coordinates now.	High	REDACTED	2026-03-01 07:28:46.330359+00
8e53d62a-46e0-405c-b535-238ae0b9fdc0	2026-01-15 17:25:48.834598+00	Tony Stark	555-0101 (Iron Line)	Status update from Wakanda. We secured a cache of Pym Particles. Sending coordinates now.	Status update from Wakanda. We secured a cache of Pym Particles. Sending coordinates now.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
73241c17-c13b-4c0c-bac5-139a01f4da72	2026-01-16 07:54:48.83464+00	Thor Odinson	555-GOD-OF-THUNDER	Status update from Sokovia. We secured a cache of Pym Particles. Sending coordinates now.	Status update from Sokovia. We secured a cache of Pym Particles. Sending coordinates now.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
4fa826c0-a45b-4c38-abb6-91109f13838e	2026-01-15 21:26:48.834693+00	Tony Stark	555-0101 (Iron Line)	Status update from Sanctum Sanctorum. We secured a cache of Pym Particles. Sending coordinates now.	Status update from Sanctum Sanctorum. We secured a cache of Pym Particles. Sending coordinates now.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
f0416e8b-ebd4-406a-b241-e9b65695ff07	2026-01-16 08:04:48.834745+00	Thor Odinson	555-GOD-OF-THUNDER	Status update from Wakanda. We secured a cache of Medical Kits. Sending coordinates now.	Status update from Wakanda. We secured a cache of Medical Kits. Sending coordinates now.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
2c554382-4e52-401d-a552-6439c9547f61	2026-01-15 23:16:48.834787+00	Tony Stark	555-0101 (Iron Line)	Urgent: Avengers Compound is critically low on Arc Reactor Cores. The civilians are worried.	Urgent: Avengers Compound is critically low on Arc Reactor Cores. The civilians are worried.	High	REDACTED	2026-03-01 07:28:46.330359+00
3fad85c0-2604-48d5-985a-8b2c29164cdf	2026-01-16 05:20:48.834955+00	Steve Rogers	555-1941 (Shield Freq)	The situation in Sokovia is dire. We need more Medical Kits or we lose the perimeter.	The situation in Sokovia is dire. We need more Medical Kits or we lose the perimeter.	High	REDACTED	2026-03-01 07:28:46.330359+00
d5354fc0-d03c-4cbf-adb8-12e917ae9728	2026-01-15 21:22:48.835162+00	Natasha Romanoff	555-0199 (Black Widow Comms)	The situation in Avengers Compound is dire. We need more Medical Kits or we lose the perimeter.	The situation in Avengers Compound is dire. We need more Medical Kits or we lose the perimeter.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
5832c8fc-74fe-4a80-9595-5168724ee9d1	2026-01-16 00:03:48.835238+00	Peter Parker	555-0123 (Spider-Sense)	Status update from Avengers Compound. We secured a cache of Pym Particles. Sending coordinates now.	Status update from Avengers Compound. We secured a cache of Pym Particles. Sending coordinates now.	High	REDACTED	2026-03-01 07:28:46.330359+00
26f11595-1f6a-4628-a47b-2ce5a2684ef8	2026-01-15 16:30:48.835302+00	Tony Stark	555-0101 (Iron Line)	The situation in Sokovia is dire. We need more Vibranium (kg) or we lose the perimeter.	The situation in Sokovia is dire. We need more Vibranium (kg) or we lose the perimeter.	High	REDACTED	2026-03-01 07:28:46.330359+00
5f52297f-fed3-4a3e-9b49-be710ccf60c4	2026-01-16 00:48:48.835364+00	Natasha Romanoff	555-0199 (Black Widow Comms)	Just a heads up, New Asgard is out of Arc Reactor Cores. This is Natasha Romanoff, call me back at 555-0199 (Black Widow Comms).	Just a heads up, New Asgard is out of Arc Reactor Cores. This is [OPERATIVE-E2AD], call me back at [CONTACT-F943].	Routine	REDACTED	2026-03-01 07:28:46.330359+00
8a4b240f-498d-4d0e-a63f-50db2f2369e2	2026-01-15 21:48:48.835424+00	Steve Rogers	555-1941 (Shield Freq)	Status update from Avengers Compound. We secured a cache of Vibranium (kg). Sending coordinates now.	Status update from Avengers Compound. We secured a cache of Vibranium (kg). Sending coordinates now.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
df29a331-94bc-4d13-9297-dd1b644eae5b	2026-01-16 08:56:48.835489+00	Bruce Banner	555-HULK-SMASH	Urgent: Sanctum Sanctorum is critically low on Arc Reactor Cores. The civilians are worried.	Urgent: Sanctum Sanctorum is critically low on Arc Reactor Cores. The civilians are worried.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
fa77e3ab-8ef4-49f4-aa65-b81c8827b251	2026-01-16 02:30:48.835553+00	Tony Stark	555-0101 (Iron Line)	Heavy combat in Avengers Compound. Vibranium (kg) supply chain is compromised. Need backup.	Heavy combat in Avengers Compound. Vibranium (kg) supply chain is compromised. Need backup.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
7252399b-0d41-41e1-a8be-a27eaa98ab70	2026-01-16 05:46:48.835615+00	Tony Stark	555-0101 (Iron Line)	The situation in Sokovia is dire. We need more Medical Kits or we lose the perimeter.	The situation in Sokovia is dire. We need more Medical Kits or we lose the perimeter.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
17caca51-a04a-4d9c-bc4b-6ca97629178b	2026-01-15 19:11:48.835684+00	Tony Stark	555-0101 (Iron Line)	Heavy combat in New Asgard. Arc Reactor Cores supply chain is compromised. Need backup.	Heavy combat in New Asgard. Arc Reactor Cores supply chain is compromised. Need backup.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
3a3d3385-2b3c-4bc6-babc-22306f46721f	2026-01-16 01:54:48.835748+00	Bruce Banner	555-HULK-SMASH	Heavy combat in Sanctum Sanctorum. Pym Particles supply chain is compromised. Need backup.	Heavy combat in Sanctum Sanctorum. Pym Particles supply chain is compromised. Need backup.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
25aeb43d-9b01-44fb-ba81-f6a8b718eb28	2026-01-16 03:22:48.835803+00	Natasha Romanoff	555-0199 (Black Widow Comms)	Heavy combat in Wakanda. Pym Particles supply chain is compromised. Need backup.	Heavy combat in Wakanda. Pym Particles supply chain is compromised. Need backup.	High	REDACTED	2026-03-01 07:28:46.330359+00
0073622f-676d-4abf-863e-c2b47f408e57	2026-01-16 08:16:48.835852+00	Bruce Banner	555-HULK-SMASH	Just a heads up, Sanctum Sanctorum is out of Vibranium (kg). This is Bruce Banner, call me back at 555-HULK-SMASH.	Just a heads up, Sanctum Sanctorum is out of Vibranium (kg). This is [OPERATIVE-726C], call me back at [CONTACT-8ED0].	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
436ea6f7-ea5e-4f23-b7dc-529bd6de814e	2026-01-16 07:30:48.835899+00	Tony Stark	555-0101 (Iron Line)	Heavy combat in Sanctum Sanctorum. Arc Reactor Cores supply chain is compromised. Need backup.	Heavy combat in Sanctum Sanctorum. Arc Reactor Cores supply chain is compromised. Need backup.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
2e3d3dc3-deb3-4521-84c7-7a2dfe269882	2026-01-16 06:35:48.835946+00	Tony Stark	555-0101 (Iron Line)	Just a heads up, New Asgard is out of Clean Water (L). This is Tony Stark, call me back at 555-0101 (Iron Line).	Just a heads up, New Asgard is out of Clean Water (L). This is [OPERATIVE-3FE0], call me back at [CONTACT-46CA].	High	REDACTED	2026-03-01 07:28:46.330359+00
ebfb714a-8e2f-401f-8063-d947cc8d14e5	2026-01-16 01:48:48.83599+00	Bruce Banner	555-HULK-SMASH	Status update from New Asgard. We secured a cache of Clean Water (L). Sending coordinates now.	Status update from New Asgard. We secured a cache of Clean Water (L). Sending coordinates now.	High	REDACTED	2026-03-01 07:28:46.330359+00
b53a84a7-9be3-47cb-931b-4546b808a2d3	2026-01-16 03:15:48.836035+00	Bruce Banner	555-HULK-SMASH	The situation in New Asgard is dire. We need more Pym Particles or we lose the perimeter.	The situation in New Asgard is dire. We need more Pym Particles or we lose the perimeter.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
5726a129-76ec-482d-a602-d3aee819e427	2026-01-16 03:43:48.836081+00	Natasha Romanoff	555-0199 (Black Widow Comms)	Just a heads up, Sanctum Sanctorum is out of Pym Particles. This is Natasha Romanoff, call me back at 555-0199 (Black Widow Comms).	Just a heads up, Sanctum Sanctorum is out of Pym Particles. This is [OPERATIVE-C5C7], call me back at [CONTACT-8F25].	Routine	REDACTED	2026-03-01 07:28:46.330359+00
fbb0768e-e8bf-417a-8619-125d9c62a3c2	2026-01-15 18:47:48.836127+00	Natasha Romanoff	555-0199 (Black Widow Comms)	Urgent: Sokovia is critically low on Vibranium (kg). The civilians are worried.	Urgent: Sokovia is critically low on Vibranium (kg). The civilians are worried.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
5d06019e-dbd8-4da1-94b5-f74be9f5f5c1	2026-01-16 02:18:48.836173+00	Peter Parker	555-0123 (Spider-Sense)	Just a heads up, Sanctum Sanctorum is out of Pym Particles. This is Peter Parker, call me back at 555-0123 (Spider-Sense).	Just a heads up, Sanctum Sanctorum is out of Pym Particles. This is [OPERATIVE-26F7], call me back at [CONTACT-FD21].	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
5f3dc400-56a3-4f20-80ef-14111db38ad3	2026-01-15 21:57:48.836218+00	Steve Rogers	555-1941 (Shield Freq)	The situation in Wakanda is dire. We need more Pym Particles or we lose the perimeter.	The situation in Wakanda is dire. We need more Pym Particles or we lose the perimeter.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
41f27429-8c61-4cf8-8b63-72dcc6425807	2026-01-15 22:33:48.836263+00	Natasha Romanoff	555-0199 (Black Widow Comms)	Heavy combat in Sokovia. Pym Particles supply chain is compromised. Need backup.	Heavy combat in Sokovia. Pym Particles supply chain is compromised. Need backup.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
36f4ad0e-fdcc-4e37-b3bf-ec747daf9fab	2026-01-16 00:13:48.836313+00	Peter Parker	555-0123 (Spider-Sense)	Heavy combat in Avengers Compound. Vibranium (kg) supply chain is compromised. Need backup.	Heavy combat in Avengers Compound. Vibranium (kg) supply chain is compromised. Need backup.	High	REDACTED	2026-03-01 07:28:46.330359+00
dc83cf17-37e0-4805-97c1-8c86a8fba4dc	2026-01-16 04:06:48.836361+00	Tony Stark	555-0101 (Iron Line)	Just a heads up, New Asgard is out of Clean Water (L). This is Tony Stark, call me back at 555-0101 (Iron Line).	Just a heads up, New Asgard is out of Clean Water (L). This is [OPERATIVE-DCA6], call me back at [CONTACT-74E5].	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
660534ec-bcac-4a16-8564-80f3a20d2321	2026-01-15 23:32:48.836406+00	Steve Rogers	555-1941 (Shield Freq)	Status update from Avengers Compound. We secured a cache of Arc Reactor Cores. Sending coordinates now.	Status update from Avengers Compound. We secured a cache of Arc Reactor Cores. Sending coordinates now.	High	REDACTED	2026-03-01 07:28:46.330359+00
d358e0d2-782b-4f2a-8878-a9b6a0c01e98	2026-01-16 06:00:48.836452+00	Steve Rogers	555-1941 (Shield Freq)	Urgent: Avengers Compound is critically low on Medical Kits. The civilians are worried.	Urgent: Avengers Compound is critically low on Medical Kits. The civilians are worried.	High	REDACTED	2026-03-01 07:28:46.330359+00
054f2286-99e9-42ab-ab74-05d577ab642c	2026-01-15 22:03:48.836499+00	Peter Parker	555-0123 (Spider-Sense)	The situation in Sanctum Sanctorum is dire. We need more Medical Kits or we lose the perimeter.	The situation in Sanctum Sanctorum is dire. We need more Medical Kits or we lose the perimeter.	High	REDACTED	2026-03-01 07:28:46.330359+00
dde682c3-e950-451b-8b64-e22fb6ac4aa1	2026-01-15 21:57:48.836542+00	Thor Odinson	555-GOD-OF-THUNDER	Urgent: New Asgard is critically low on Clean Water (L). The civilians are worried.	Urgent: New Asgard is critically low on Clean Water (L). The civilians are worried.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
22cec2ec-7203-41d8-9f6a-a11a9c47ca43	2026-01-15 20:57:48.836591+00	Steve Rogers	555-1941 (Shield Freq)	The situation in Sanctum Sanctorum is dire. We need more Clean Water (L) or we lose the perimeter.	The situation in Sanctum Sanctorum is dire. We need more Clean Water (L) or we lose the perimeter.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
c67844fa-4568-4150-9c08-045cb9f1a24f	2026-01-16 03:38:48.836656+00	Bruce Banner	555-HULK-SMASH	Status update from Avengers Compound. We secured a cache of Clean Water (L). Sending coordinates now.	Status update from Avengers Compound. We secured a cache of Clean Water (L). Sending coordinates now.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
f9c76280-2497-44d6-a9e2-9e75d4b4d31c	2026-01-15 23:52:48.8367+00	Peter Parker	555-0123 (Spider-Sense)	The situation in Sanctum Sanctorum is dire. We need more Vibranium (kg) or we lose the perimeter.	The situation in Sanctum Sanctorum is dire. We need more Vibranium (kg) or we lose the perimeter.	High	REDACTED	2026-03-01 07:28:46.330359+00
5f36cff4-68d0-4e6d-9180-0e1f7fdc359d	2026-01-16 00:10:48.836744+00	Thor Odinson	555-GOD-OF-THUNDER	Heavy combat in Sanctum Sanctorum. Vibranium (kg) supply chain is compromised. Need backup.	Heavy combat in Sanctum Sanctorum. Vibranium (kg) supply chain is compromised. Need backup.	High	REDACTED	2026-03-01 07:28:46.330359+00
bbe81d1a-79c3-4156-a1c5-76f30cc15d7d	2026-01-16 07:39:48.836792+00	Thor Odinson	555-GOD-OF-THUNDER	Just a heads up, Sokovia is out of Vibranium (kg). This is Thor Odinson, call me back at 555-GOD-OF-THUNDER.	Just a heads up, Sokovia is out of Vibranium (kg). This is [OPERATIVE-D6B9], call me back at [CONTACT-31F6].	High	REDACTED	2026-03-01 07:28:46.330359+00
438856ae-cb9d-4d1e-ae13-88856f2d060c	2026-01-16 00:31:48.836843+00	Bruce Banner	555-HULK-SMASH	Just a heads up, Wakanda is out of Clean Water (L). This is Bruce Banner, call me back at 555-HULK-SMASH.	Just a heads up, Wakanda is out of Clean Water (L). This is [OPERATIVE-E7A6], call me back at [CONTACT-1C35].	High	REDACTED	2026-03-01 07:28:46.330359+00
aea8fa9d-d66e-4def-8f1a-579b29cf9d8f	2026-01-15 16:52:48.836891+00	Natasha Romanoff	555-0199 (Black Widow Comms)	The situation in New Asgard is dire. We need more Arc Reactor Cores or we lose the perimeter.	The situation in New Asgard is dire. We need more Arc Reactor Cores or we lose the perimeter.	High	REDACTED	2026-03-01 07:28:46.330359+00
c613500c-a48c-488d-a16d-32fa13a7f34a	2026-01-16 04:54:48.836937+00	Natasha Romanoff	555-0199 (Black Widow Comms)	Heavy combat in Wakanda. Clean Water (L) supply chain is compromised. Need backup.	Heavy combat in Wakanda. Clean Water (L) supply chain is compromised. Need backup.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
271073e8-771f-440f-aac0-dca4f51189f6	2026-01-16 03:10:48.836983+00	Thor Odinson	555-GOD-OF-THUNDER	Status update from Avengers Compound. We secured a cache of Vibranium (kg). Sending coordinates now.	Status update from Avengers Compound. We secured a cache of Vibranium (kg). Sending coordinates now.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
0be1e38e-0f5a-48cc-888b-9ad854995c21	2026-01-16 08:03:48.837029+00	Bruce Banner	555-HULK-SMASH	Just a heads up, Wakanda is out of Clean Water (L). This is Bruce Banner, call me back at 555-HULK-SMASH.	Just a heads up, Wakanda is out of Clean Water (L). This is [OPERATIVE-C2D0], call me back at [CONTACT-DE78].	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
1b4f7007-9552-4582-8aba-cb3a92085ba7	2026-01-15 20:47:48.837074+00	Natasha Romanoff	555-0199 (Black Widow Comms)	Status update from Sokovia. We secured a cache of Medical Kits. Sending coordinates now.	Status update from Sokovia. We secured a cache of Medical Kits. Sending coordinates now.	High	REDACTED	2026-03-01 07:28:46.330359+00
aac4e797-0578-4368-b485-a067abd7b0a1	2026-01-16 04:54:48.837119+00	Peter Parker	555-0123 (Spider-Sense)	Urgent: Sokovia is critically low on Pym Particles. The civilians are worried.	Urgent: Sokovia is critically low on Pym Particles. The civilians are worried.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
ad0ba7ba-5af1-4c87-8e15-f96523247478	2026-01-15 16:43:48.837164+00	Thor Odinson	555-GOD-OF-THUNDER	Just a heads up, Sokovia is out of Pym Particles. This is Thor Odinson, call me back at 555-GOD-OF-THUNDER.	Just a heads up, Sokovia is out of Pym Particles. This is [OPERATIVE-96B3], call me back at [CONTACT-D818].	High	REDACTED	2026-03-01 07:28:46.330359+00
f73ab4a3-9b02-44a8-9604-a1a443964e0d	2026-01-15 21:02:48.837211+00	Thor Odinson	555-GOD-OF-THUNDER	The situation in Sanctum Sanctorum is dire. We need more Pym Particles or we lose the perimeter.	The situation in Sanctum Sanctorum is dire. We need more Pym Particles or we lose the perimeter.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
98af3bf4-d742-4801-a5ea-c2f50db933fe	2026-01-16 05:36:48.837258+00	Bruce Banner	555-HULK-SMASH	The situation in New Asgard is dire. We need more Vibranium (kg) or we lose the perimeter.	The situation in New Asgard is dire. We need more Vibranium (kg) or we lose the perimeter.	High	REDACTED	2026-03-01 07:28:46.330359+00
3aae0784-9750-4d0a-bafe-8504656fe062	2026-01-16 02:13:48.837308+00	Natasha Romanoff	555-0199 (Black Widow Comms)	Heavy combat in Avengers Compound. Medical Kits supply chain is compromised. Need backup.	Heavy combat in Avengers Compound. Medical Kits supply chain is compromised. Need backup.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
cdc10eec-2f56-4850-b5e2-d30d64b0c926	2026-01-16 05:08:48.837358+00	Natasha Romanoff	555-0199 (Black Widow Comms)	Heavy combat in Avengers Compound. Pym Particles supply chain is compromised. Need backup.	Heavy combat in Avengers Compound. Pym Particles supply chain is compromised. Need backup.	High	REDACTED	2026-03-01 07:28:46.330359+00
f3cdeb8a-ee55-4c2c-b18b-9e0ef202e54f	2026-01-16 08:56:48.837405+00	Tony Stark	555-0101 (Iron Line)	Heavy combat in New Asgard. Arc Reactor Cores supply chain is compromised. Need backup.	Heavy combat in New Asgard. Arc Reactor Cores supply chain is compromised. Need backup.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
01fa9156-0de2-4180-8125-5b409d8a387c	2026-01-15 23:20:48.837456+00	Thor Odinson	555-GOD-OF-THUNDER	The situation in New Asgard is dire. We need more Arc Reactor Cores or we lose the perimeter.	The situation in New Asgard is dire. We need more Arc Reactor Cores or we lose the perimeter.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
a8e24d5b-d1e6-4739-b36a-44cce54e1af1	2026-01-15 20:21:48.837503+00	Thor Odinson	555-GOD-OF-THUNDER	Heavy combat in Sokovia. Medical Kits supply chain is compromised. Need backup.	Heavy combat in Sokovia. Medical Kits supply chain is compromised. Need backup.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
4b3f57b2-85f3-49e0-95f8-1a0b2ef7faee	2026-01-16 04:35:48.837553+00	Steve Rogers	555-1941 (Shield Freq)	Urgent: Sanctum Sanctorum is critically low on Clean Water (L). The civilians are worried.	Urgent: Sanctum Sanctorum is critically low on Clean Water (L). The civilians are worried.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
1ec710d7-f5e0-433c-867f-0c0a4fc95155	2026-01-15 19:35:48.837607+00	Tony Stark	555-0101 (Iron Line)	Just a heads up, Sanctum Sanctorum is out of Arc Reactor Cores. This is Tony Stark, call me back at 555-0101 (Iron Line).	Just a heads up, Sanctum Sanctorum is out of Arc Reactor Cores. This is [OPERATIVE-A85A], call me back at [CONTACT-94BD].	Routine	REDACTED	2026-03-01 07:28:46.330359+00
65f4838f-1eea-48e3-bb8c-0b6b741504ee	2026-01-16 06:23:48.837658+00	Peter Parker	555-0123 (Spider-Sense)	Just a heads up, Avengers Compound is out of Arc Reactor Cores. This is Peter Parker, call me back at 555-0123 (Spider-Sense).	Just a heads up, Avengers Compound is out of Arc Reactor Cores. This is [OPERATIVE-4E98], call me back at [CONTACT-482F].	High	REDACTED	2026-03-01 07:28:46.330359+00
402cdcc1-0cd0-4726-ad24-5867112628fc	2026-01-15 19:55:48.837707+00	Peter Parker	555-0123 (Spider-Sense)	Urgent: Wakanda is critically low on Clean Water (L). The civilians are worried.	Urgent: Wakanda is critically low on Clean Water (L). The civilians are worried.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
167acffc-523a-4bf4-a8f2-2cc2cced8b26	2026-01-15 16:48:48.837753+00	Bruce Banner	555-HULK-SMASH	Heavy combat in New Asgard. Arc Reactor Cores supply chain is compromised. Need backup.	Heavy combat in New Asgard. Arc Reactor Cores supply chain is compromised. Need backup.	Routine	REDACTED	2026-03-01 07:28:46.330359+00
31d4d52d-151e-4cef-9bcf-fa8516aaab1c	2026-01-15 23:52:48.837796+00	Bruce Banner	555-HULK-SMASH	Urgent: Sokovia is critically low on Vibranium (kg). The civilians are worried.	Urgent: Sokovia is critically low on Vibranium (kg). The civilians are worried.	High	REDACTED	2026-03-01 07:28:46.330359+00
359ab88c-64ea-44a5-9365-2affaf5a91d6	2026-01-16 08:38:48.837843+00	Tony Stark	555-0101 (Iron Line)	Urgent: Sanctum Sanctorum is critically low on Arc Reactor Cores. The civilians are worried.	Urgent: Sanctum Sanctorum is critically low on Arc Reactor Cores. The civilians are worried.	High	REDACTED	2026-03-01 07:28:46.330359+00
2f03e506-70ae-4fd9-a7d3-0b95daa6e58e	2026-01-16 07:41:48.837893+00	Natasha Romanoff	555-0199 (Black Widow Comms)	Heavy combat in Wakanda. Clean Water (L) supply chain is compromised. Need backup.	Heavy combat in Wakanda. Clean Water (L) supply chain is compromised. Need backup.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
df5c6b28-7317-44bd-8145-11b333a56254	2026-01-15 19:58:48.83794+00	Natasha Romanoff	555-0199 (Black Widow Comms)	Just a heads up, New Asgard is out of Vibranium (kg). This is Natasha Romanoff, call me back at 555-0199 (Black Widow Comms).	Just a heads up, New Asgard is out of Vibranium (kg). This is [OPERATIVE-B578], call me back at [CONTACT-99AE].	Routine	REDACTED	2026-03-01 07:28:46.330359+00
a2ca8dee-8c97-4cae-876b-d0c3120b67fa	2026-01-16 03:10:48.837988+00	Peter Parker	555-0123 (Spider-Sense)	Just a heads up, Wakanda is out of Medical Kits. This is Peter Parker, call me back at 555-0123 (Spider-Sense).	Just a heads up, Wakanda is out of Medical Kits. This is [OPERATIVE-5B3B], call me back at [CONTACT-8AA0].	Routine	REDACTED	2026-03-01 07:28:46.330359+00
1e986b6f-9cab-4fdc-b5a6-f8406e494ea2	2026-01-15 23:17:48.838032+00	Bruce Banner	555-HULK-SMASH	Urgent: Sanctum Sanctorum is critically low on Medical Kits. The civilians are worried.	Urgent: Sanctum Sanctorum is critically low on Medical Kits. The civilians are worried.	Avengers Level Threat	REDACTED	2026-03-01 07:28:46.330359+00
c6adce54-36db-4505-8a58-eab02fe9bc1f	2026-01-15 18:22:48.838094+00	Thor Odinson	555-GOD-OF-THUNDER	Just a heads up, Wakanda is out of Medical Kits. This is Thor Odinson, call me back at 555-GOD-OF-THUNDER.	Just a heads up, Wakanda is out of Medical Kits. This is [OPERATIVE-EE8F], call me back at [CONTACT-E086].	High	REDACTED	2026-03-01 07:28:46.330359+00
\.


--
-- Name: intel_extracted_id_seq; Type: SEQUENCE SET; Schema: public; Owner: edith_user
--

SELECT pg_catalog.setval('public.intel_extracted_id_seq', 1, false);


--
-- Name: redaction_audit_id_seq; Type: SEQUENCE SET; Schema: public; Owner: edith_user
--

SELECT pg_catalog.setval('public.redaction_audit_id_seq', 68, true);


--
-- Name: intel_extracted intel_extracted_pkey; Type: CONSTRAINT; Schema: public; Owner: edith_user
--

ALTER TABLE ONLY public.intel_extracted
    ADD CONSTRAINT intel_extracted_pkey PRIMARY KEY (id);


--
-- Name: redaction_audit redaction_audit_pkey; Type: CONSTRAINT; Schema: public; Owner: edith_user
--

ALTER TABLE ONLY public.redaction_audit
    ADD CONSTRAINT redaction_audit_pkey PRIMARY KEY (id);


--
-- Name: reports reports_pkey; Type: CONSTRAINT; Schema: public; Owner: edith_user
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_pkey PRIMARY KEY (report_id);


--
-- Name: intel_extracted intel_extracted_report_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: edith_user
--

ALTER TABLE ONLY public.intel_extracted
    ADD CONSTRAINT intel_extracted_report_id_fkey FOREIGN KEY (report_id) REFERENCES public.reports(report_id);


--
-- Name: redaction_audit redaction_audit_report_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: edith_user
--

ALTER TABLE ONLY public.redaction_audit
    ADD CONSTRAINT redaction_audit_report_id_fkey FOREIGN KEY (report_id) REFERENCES public.reports(report_id);


--
-- PostgreSQL database dump complete
--

\unrestrict 7jh7pmeBDKM7C64E2k2uRb2ZhDZd8kkqa2HwekT6KLIeQUL7wmsQrssfrOqYp0m

