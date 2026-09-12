--
-- PostgreSQL database dump
--

\restrict ucWj8IzFgpv5QiFqd0BdHQoK4yOfgQZdwFoIbwnkZ2PLKaWdUR57dy341K6QFAN

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.teachers_teacher DROP CONSTRAINT IF EXISTS teachers_teacher_salary_scale_id_e526c2c8_fk_teachers_;
ALTER TABLE IF EXISTS ONLY public.teachers_monthlysalarybill DROP CONSTRAINT IF EXISTS teachers_monthlysala_teacher_id_cc1084ca_fk_teachers_;
ALTER TABLE IF EXISTS ONLY public.students_student DROP CONSTRAINT IF EXISTS students_student_family_id_bbc9cc99_fk_students_;
ALTER TABLE IF EXISTS ONLY public.students_student DROP CONSTRAINT IF EXISTS students_student_current_section_id_3239129f_fk_school_se;
ALTER TABLE IF EXISTS ONLY public.students_student DROP CONSTRAINT IF EXISTS students_student_current_class_id_cf5f558b_fk_school_cl;
ALTER TABLE IF EXISTS ONLY public.students_promotionhistory DROP CONSTRAINT IF EXISTS students_promotionhi_to_section_id_ec1f7bb7_fk_school_se;
ALTER TABLE IF EXISTS ONLY public.students_promotionhistory DROP CONSTRAINT IF EXISTS students_promotionhi_to_class_id_d284316c_fk_school_cl;
ALTER TABLE IF EXISTS ONLY public.students_promotionhistory DROP CONSTRAINT IF EXISTS students_promotionhi_student_id_66feb5eb_fk_students_;
ALTER TABLE IF EXISTS ONLY public.students_promotionhistory DROP CONSTRAINT IF EXISTS students_promotionhi_from_section_id_9305de88_fk_school_se;
ALTER TABLE IF EXISTS ONLY public.students_promotionhistory DROP CONSTRAINT IF EXISTS students_promotionhi_from_class_id_7189d79c_fk_school_cl;
ALTER TABLE IF EXISTS ONLY public.school_section DROP CONSTRAINT IF EXISTS school_section_class_level_id_0c997e4a_fk_school_classlevel_id;
ALTER TABLE IF EXISTS ONLY public.finance_studentfeemonthentry DROP CONSTRAINT IF EXISTS finance_studentfeemo_ledger_id_e4c9a9e7_fk_finance_s;
ALTER TABLE IF EXISTS ONLY public.finance_studentfeeledger DROP CONSTRAINT IF EXISTS finance_studentfeele_student_id_6819ba4c_fk_students_;
ALTER TABLE IF EXISTS ONLY public.finance_studentfeeledger DROP CONSTRAINT IF EXISTS finance_studentfeele_academic_session_id_98fdaaac_fk_school_ac;
ALTER TABLE IF EXISTS ONLY public.finance_feepaymentreceipt_month_entries DROP CONSTRAINT IF EXISTS finance_feepaymentre_studentfeemonthentry_88f8f2aa_fk_finance_s;
ALTER TABLE IF EXISTS ONLY public.finance_feepaymentreceipt DROP CONSTRAINT IF EXISTS finance_feepaymentre_student_id_0286c392_fk_students_;
ALTER TABLE IF EXISTS ONLY public.finance_feepaymentreceipt_month_entries DROP CONSTRAINT IF EXISTS finance_feepaymentre_feepaymentreceipt_id_8da561d4_fk_finance_f;
ALTER TABLE IF EXISTS ONLY public.exams_exammark DROP CONSTRAINT IF EXISTS exams_exammark_subject_id_b114cf98_fk_exams_subject_id;
ALTER TABLE IF EXISTS ONLY public.exams_exammark DROP CONSTRAINT IF EXISTS exams_exammark_student_id_fcc2fb05_fk_students_student_id;
ALTER TABLE IF EXISTS ONLY public.exams_exammark DROP CONSTRAINT IF EXISTS exams_exammark_exam_id_0e1ee69b_fk_exams_exam_id;
ALTER TABLE IF EXISTS ONLY public.exams_exammark DROP CONSTRAINT IF EXISTS exams_exammark_class_level_id_9d13595d_fk_school_classlevel_id;
ALTER TABLE IF EXISTS ONLY public.exams_exam DROP CONSTRAINT IF EXISTS exams_exam_session_id_97602d19_fk_school_academicsession_id;
ALTER TABLE IF EXISTS ONLY public.exams_classsubject DROP CONSTRAINT IF EXISTS exams_classsubject_subject_id_c4ba1111_fk_exams_subject_id;
ALTER TABLE IF EXISTS ONLY public.exams_classsubject DROP CONSTRAINT IF EXISTS exams_classsubject_class_level_id_1cf805ba_fk_school_cl;
ALTER TABLE IF EXISTS ONLY public.django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_user_id_c564eba6_fk_auth_user_id;
ALTER TABLE IF EXISTS ONLY public.django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_content_type_id_c4bce8eb_fk_django_co;
ALTER TABLE IF EXISTS ONLY public.auth_user_user_permissions DROP CONSTRAINT IF EXISTS auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id;
ALTER TABLE IF EXISTS ONLY public.auth_user_user_permissions DROP CONSTRAINT IF EXISTS auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm;
ALTER TABLE IF EXISTS ONLY public.auth_user_groups DROP CONSTRAINT IF EXISTS auth_user_groups_user_id_6a12ed8b_fk_auth_user_id;
ALTER TABLE IF EXISTS ONLY public.auth_user_groups DROP CONSTRAINT IF EXISTS auth_user_groups_group_id_97559544_fk_auth_group_id;
ALTER TABLE IF EXISTS ONLY public.auth_permission DROP CONSTRAINT IF EXISTS auth_permission_content_type_id_2f476e4b_fk_django_co;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissions_group_id_b120cbf9_fk_auth_group_id;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissio_permission_id_84c5c92e_fk_auth_perm;
DROP INDEX IF EXISTS public.teachers_teacher_teacher_id_d2057e5f_like;
DROP INDEX IF EXISTS public.teachers_teacher_salary_scale_id_e526c2c8;
DROP INDEX IF EXISTS public.teachers_salaryscale_name_829c87a9_like;
DROP INDEX IF EXISTS public.teachers_monthlysalarybill_teacher_id_cc1084ca;
DROP INDEX IF EXISTS public.students_student_family_id_bbc9cc99;
DROP INDEX IF EXISTS public.students_student_current_section_id_3239129f;
DROP INDEX IF EXISTS public.students_student_current_class_id_cf5f558b;
DROP INDEX IF EXISTS public.students_student_admission_no_feb174a2_like;
DROP INDEX IF EXISTS public.students_promotionhistory_to_section_id_ec1f7bb7;
DROP INDEX IF EXISTS public.students_promotionhistory_to_class_id_d284316c;
DROP INDEX IF EXISTS public.students_promotionhistory_student_id_66feb5eb;
DROP INDEX IF EXISTS public.students_promotionhistory_from_section_id_9305de88;
DROP INDEX IF EXISTS public.students_promotionhistory_from_class_id_7189d79c;
DROP INDEX IF EXISTS public.students_familyhousehold_family_id_0db3cd5b_like;
DROP INDEX IF EXISTS public.school_section_class_level_id_0c997e4a;
DROP INDEX IF EXISTS public.school_classlevel_name_45e68f6f_like;
DROP INDEX IF EXISTS public.school_academicsession_name_f698a586_like;
DROP INDEX IF EXISTS public.finance_studentfeemonthentry_ledger_id_e4c9a9e7;
DROP INDEX IF EXISTS public.finance_studentfeeledger_student_id_6819ba4c;
DROP INDEX IF EXISTS public.finance_studentfeeledger_academic_session_id_98fdaaac;
DROP INDEX IF EXISTS public.finance_feepaymentreceipt_student_id_0286c392;
DROP INDEX IF EXISTS public.finance_feepaymentreceipt_receipt_no_2a5aaf5c_like;
DROP INDEX IF EXISTS public.finance_feepaymentreceipt__studentfeemonthentry_id_88f8f2aa;
DROP INDEX IF EXISTS public.finance_feepaymentreceipt__feepaymentreceipt_id_8da561d4;
DROP INDEX IF EXISTS public.exams_subject_name_ec73097d_like;
DROP INDEX IF EXISTS public.exams_exammark_subject_id_b114cf98;
DROP INDEX IF EXISTS public.exams_exammark_student_id_fcc2fb05;
DROP INDEX IF EXISTS public.exams_exammark_exam_id_0e1ee69b;
DROP INDEX IF EXISTS public.exams_exammark_class_level_id_9d13595d;
DROP INDEX IF EXISTS public.exams_exam_session_id_97602d19;
DROP INDEX IF EXISTS public.exams_classsubject_subject_id_c4ba1111;
DROP INDEX IF EXISTS public.exams_classsubject_class_level_id_1cf805ba;
DROP INDEX IF EXISTS public.django_session_session_key_c0390e0f_like;
DROP INDEX IF EXISTS public.django_session_expire_date_a5c62663;
DROP INDEX IF EXISTS public.django_admin_log_user_id_c564eba6;
DROP INDEX IF EXISTS public.django_admin_log_content_type_id_c4bce8eb;
DROP INDEX IF EXISTS public.auth_user_username_6821ab7c_like;
DROP INDEX IF EXISTS public.auth_user_user_permissions_user_id_a95ead1b;
DROP INDEX IF EXISTS public.auth_user_user_permissions_permission_id_1fbb5f2c;
DROP INDEX IF EXISTS public.auth_user_groups_user_id_6a12ed8b;
DROP INDEX IF EXISTS public.auth_user_groups_group_id_97559544;
DROP INDEX IF EXISTS public.auth_permission_content_type_id_2f476e4b;
DROP INDEX IF EXISTS public.auth_group_permissions_permission_id_84c5c92e;
DROP INDEX IF EXISTS public.auth_group_permissions_group_id_b120cbf9;
DROP INDEX IF EXISTS public.auth_group_name_a6ea08ec_like;
ALTER TABLE IF EXISTS ONLY public.teachers_teacher DROP CONSTRAINT IF EXISTS teachers_teacher_teacher_id_key;
ALTER TABLE IF EXISTS ONLY public.teachers_teacher DROP CONSTRAINT IF EXISTS teachers_teacher_pkey;
ALTER TABLE IF EXISTS ONLY public.teachers_salaryscale DROP CONSTRAINT IF EXISTS teachers_salaryscale_pkey;
ALTER TABLE IF EXISTS ONLY public.teachers_salaryscale DROP CONSTRAINT IF EXISTS teachers_salaryscale_name_key;
ALTER TABLE IF EXISTS ONLY public.teachers_monthlysalarybill DROP CONSTRAINT IF EXISTS teachers_monthlysalarybill_teacher_id_month_year_6e9825e4_uniq;
ALTER TABLE IF EXISTS ONLY public.teachers_monthlysalarybill DROP CONSTRAINT IF EXISTS teachers_monthlysalarybill_pkey;
ALTER TABLE IF EXISTS ONLY public.students_student DROP CONSTRAINT IF EXISTS students_student_pkey;
ALTER TABLE IF EXISTS ONLY public.students_student DROP CONSTRAINT IF EXISTS students_student_admission_no_key;
ALTER TABLE IF EXISTS ONLY public.students_promotionhistory DROP CONSTRAINT IF EXISTS students_promotionhistory_pkey;
ALTER TABLE IF EXISTS ONLY public.students_familyhousehold DROP CONSTRAINT IF EXISTS students_familyhousehold_pkey;
ALTER TABLE IF EXISTS ONLY public.students_familyhousehold DROP CONSTRAINT IF EXISTS students_familyhousehold_family_id_key;
ALTER TABLE IF EXISTS ONLY public.school_section DROP CONSTRAINT IF EXISTS school_section_pkey;
ALTER TABLE IF EXISTS ONLY public.school_section DROP CONSTRAINT IF EXISTS school_section_class_level_id_name_bdec3baa_uniq;
ALTER TABLE IF EXISTS ONLY public.school_schoolsetting DROP CONSTRAINT IF EXISTS school_schoolsetting_pkey;
ALTER TABLE IF EXISTS ONLY public.school_classlevel DROP CONSTRAINT IF EXISTS school_classlevel_pkey;
ALTER TABLE IF EXISTS ONLY public.school_classlevel DROP CONSTRAINT IF EXISTS school_classlevel_name_key;
ALTER TABLE IF EXISTS ONLY public.school_academicsession DROP CONSTRAINT IF EXISTS school_academicsession_pkey;
ALTER TABLE IF EXISTS ONLY public.school_academicsession DROP CONSTRAINT IF EXISTS school_academicsession_name_key;
ALTER TABLE IF EXISTS ONLY public.finance_studentfeemonthentry DROP CONSTRAINT IF EXISTS finance_studentfeemonthentry_pkey;
ALTER TABLE IF EXISTS ONLY public.finance_studentfeemonthentry DROP CONSTRAINT IF EXISTS finance_studentfeemonthentry_ledger_id_month_9462bee3_uniq;
ALTER TABLE IF EXISTS ONLY public.finance_studentfeeledger DROP CONSTRAINT IF EXISTS finance_studentfeeledger_student_id_academic_sess_851f7590_uniq;
ALTER TABLE IF EXISTS ONLY public.finance_studentfeeledger DROP CONSTRAINT IF EXISTS finance_studentfeeledger_pkey;
ALTER TABLE IF EXISTS ONLY public.finance_feepaymentreceipt DROP CONSTRAINT IF EXISTS finance_feepaymentreceipt_receipt_no_key;
ALTER TABLE IF EXISTS ONLY public.finance_feepaymentreceipt DROP CONSTRAINT IF EXISTS finance_feepaymentreceipt_pkey;
ALTER TABLE IF EXISTS ONLY public.finance_feepaymentreceipt_month_entries DROP CONSTRAINT IF EXISTS finance_feepaymentreceipt_month_entries_pkey;
ALTER TABLE IF EXISTS ONLY public.finance_feepaymentreceipt_month_entries DROP CONSTRAINT IF EXISTS finance_feepaymentreceip_feepaymentreceipt_id_stu_5fa12f1a_uniq;
ALTER TABLE IF EXISTS ONLY public.exams_subject DROP CONSTRAINT IF EXISTS exams_subject_pkey;
ALTER TABLE IF EXISTS ONLY public.exams_subject DROP CONSTRAINT IF EXISTS exams_subject_name_key;
ALTER TABLE IF EXISTS ONLY public.exams_exammark DROP CONSTRAINT IF EXISTS exams_exammark_pkey;
ALTER TABLE IF EXISTS ONLY public.exams_exammark DROP CONSTRAINT IF EXISTS exams_exammark_exam_id_student_id_subject_id_9db8e81e_uniq;
ALTER TABLE IF EXISTS ONLY public.exams_exam DROP CONSTRAINT IF EXISTS exams_exam_pkey;
ALTER TABLE IF EXISTS ONLY public.exams_classsubject DROP CONSTRAINT IF EXISTS exams_classsubject_pkey;
ALTER TABLE IF EXISTS ONLY public.exams_classsubject DROP CONSTRAINT IF EXISTS exams_classsubject_class_level_id_subject_id_78b4658b_uniq;
ALTER TABLE IF EXISTS ONLY public.django_session DROP CONSTRAINT IF EXISTS django_session_pkey;
ALTER TABLE IF EXISTS ONLY public.django_migrations DROP CONSTRAINT IF EXISTS django_migrations_pkey;
ALTER TABLE IF EXISTS ONLY public.django_content_type DROP CONSTRAINT IF EXISTS django_content_type_pkey;
ALTER TABLE IF EXISTS ONLY public.django_content_type DROP CONSTRAINT IF EXISTS django_content_type_app_label_model_76bd3d3b_uniq;
ALTER TABLE IF EXISTS ONLY public.django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_user DROP CONSTRAINT IF EXISTS auth_user_username_key;
ALTER TABLE IF EXISTS ONLY public.auth_user_user_permissions DROP CONSTRAINT IF EXISTS auth_user_user_permissions_user_id_permission_id_14a6b632_uniq;
ALTER TABLE IF EXISTS ONLY public.auth_user_user_permissions DROP CONSTRAINT IF EXISTS auth_user_user_permissions_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_user DROP CONSTRAINT IF EXISTS auth_user_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_user_groups DROP CONSTRAINT IF EXISTS auth_user_groups_user_id_group_id_94350c0c_uniq;
ALTER TABLE IF EXISTS ONLY public.auth_user_groups DROP CONSTRAINT IF EXISTS auth_user_groups_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_permission DROP CONSTRAINT IF EXISTS auth_permission_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_permission DROP CONSTRAINT IF EXISTS auth_permission_content_type_id_codename_01ab375a_uniq;
ALTER TABLE IF EXISTS ONLY public.auth_group DROP CONSTRAINT IF EXISTS auth_group_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissions_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissions_group_id_permission_id_0cd325b0_uniq;
ALTER TABLE IF EXISTS ONLY public.auth_group DROP CONSTRAINT IF EXISTS auth_group_name_key;
ALTER TABLE IF EXISTS ONLY public.accounts_expense DROP CONSTRAINT IF EXISTS accounts_expense_pkey;
DROP TABLE IF EXISTS public.teachers_teacher;
DROP TABLE IF EXISTS public.teachers_salaryscale;
DROP TABLE IF EXISTS public.teachers_monthlysalarybill;
DROP TABLE IF EXISTS public.students_student;
DROP TABLE IF EXISTS public.students_promotionhistory;
DROP TABLE IF EXISTS public.students_familyhousehold;
DROP TABLE IF EXISTS public.school_section;
DROP TABLE IF EXISTS public.school_schoolsetting;
DROP TABLE IF EXISTS public.school_classlevel;
DROP TABLE IF EXISTS public.school_academicsession;
DROP TABLE IF EXISTS public.finance_studentfeemonthentry;
DROP TABLE IF EXISTS public.finance_studentfeeledger;
DROP TABLE IF EXISTS public.finance_feepaymentreceipt_month_entries;
DROP TABLE IF EXISTS public.finance_feepaymentreceipt;
DROP TABLE IF EXISTS public.exams_subject;
DROP TABLE IF EXISTS public.exams_exammark;
DROP TABLE IF EXISTS public.exams_exam;
DROP TABLE IF EXISTS public.exams_classsubject;
DROP TABLE IF EXISTS public.django_session;
DROP TABLE IF EXISTS public.django_migrations;
DROP TABLE IF EXISTS public.django_content_type;
DROP TABLE IF EXISTS public.django_admin_log;
DROP TABLE IF EXISTS public.auth_user_user_permissions;
DROP TABLE IF EXISTS public.auth_user_groups;
DROP TABLE IF EXISTS public.auth_user;
DROP TABLE IF EXISTS public.auth_permission;
DROP TABLE IF EXISTS public.auth_group_permissions;
DROP TABLE IF EXISTS public.auth_group;
DROP TABLE IF EXISTS public.accounts_expense;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: accounts_expense; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.accounts_expense (
    id bigint NOT NULL,
    date date NOT NULL,
    category character varying(50) NOT NULL,
    amount numeric(10,2) NOT NULL,
    note text NOT NULL,
    reference character varying(50) NOT NULL,
    payment_mode character varying(20) NOT NULL
);


ALTER TABLE public.accounts_expense OWNER TO postgres;

--
-- Name: accounts_expense_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.accounts_expense ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.accounts_expense_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);


ALTER TABLE public.auth_group OWNER TO postgres;

--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.auth_group ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_group_permissions (
    id bigint NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_group_permissions OWNER TO postgres;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.auth_group_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE public.auth_permission OWNER TO postgres;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.auth_permission ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_user (
    id integer NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(150) NOT NULL,
    first_name character varying(150) NOT NULL,
    last_name character varying(150) NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL
);


ALTER TABLE public.auth_user OWNER TO postgres;

--
-- Name: auth_user_groups; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_user_groups (
    id bigint NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE public.auth_user_groups OWNER TO postgres;

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.auth_user_groups ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.auth_user ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_user_user_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_user_user_permissions (
    id bigint NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_user_user_permissions OWNER TO postgres;

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.auth_user_user_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


ALTER TABLE public.django_admin_log OWNER TO postgres;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.django_admin_log ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE public.django_content_type OWNER TO postgres;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.django_content_type ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_migrations (
    id bigint NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE public.django_migrations OWNER TO postgres;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.django_migrations ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


ALTER TABLE public.django_session OWNER TO postgres;

--
-- Name: exams_classsubject; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exams_classsubject (
    id bigint NOT NULL,
    total_marks numeric(5,1) NOT NULL,
    passing_marks numeric(5,1) NOT NULL,
    "order" integer NOT NULL,
    class_level_id bigint NOT NULL,
    subject_id bigint NOT NULL
);


ALTER TABLE public.exams_classsubject OWNER TO postgres;

--
-- Name: exams_classsubject_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.exams_classsubject ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.exams_classsubject_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: exams_exam; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exams_exam (
    id bigint NOT NULL,
    name character varying(150) NOT NULL,
    start_date date,
    end_date date,
    is_active boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    session_id bigint NOT NULL
);


ALTER TABLE public.exams_exam OWNER TO postgres;

--
-- Name: exams_exam_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.exams_exam ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.exams_exam_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: exams_exammark; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exams_exammark (
    id bigint NOT NULL,
    total_marks numeric(5,1) NOT NULL,
    obtained_marks numeric(5,1) NOT NULL,
    is_absent boolean NOT NULL,
    remarks character varying(100) NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    class_level_id bigint NOT NULL,
    exam_id bigint NOT NULL,
    student_id bigint NOT NULL,
    subject_id bigint NOT NULL
);


ALTER TABLE public.exams_exammark OWNER TO postgres;

--
-- Name: exams_exammark_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.exams_exammark ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.exams_exammark_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: exams_subject; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exams_subject (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    code character varying(20) NOT NULL,
    "order" integer NOT NULL,
    is_active boolean NOT NULL
);


ALTER TABLE public.exams_subject OWNER TO postgres;

--
-- Name: exams_subject_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.exams_subject ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.exams_subject_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: finance_feepaymentreceipt; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.finance_feepaymentreceipt (
    id bigint NOT NULL,
    receipt_no character varying(50) NOT NULL,
    payment_date date NOT NULL,
    amount_paid numeric(10,2) NOT NULL,
    remarks text NOT NULL,
    student_id bigint NOT NULL
);


ALTER TABLE public.finance_feepaymentreceipt OWNER TO postgres;

--
-- Name: finance_feepaymentreceipt_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.finance_feepaymentreceipt ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.finance_feepaymentreceipt_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: finance_feepaymentreceipt_month_entries; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.finance_feepaymentreceipt_month_entries (
    id bigint NOT NULL,
    feepaymentreceipt_id bigint CONSTRAINT finance_feepaymentreceipt_month_e_feepaymentreceipt_id_not_null NOT NULL,
    studentfeemonthentry_id bigint CONSTRAINT finance_feepaymentreceipt_mont_studentfeemonthentry_id_not_null NOT NULL
);


ALTER TABLE public.finance_feepaymentreceipt_month_entries OWNER TO postgres;

--
-- Name: finance_feepaymentreceipt_month_entries_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.finance_feepaymentreceipt_month_entries ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.finance_feepaymentreceipt_month_entries_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: finance_studentfeeledger; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.finance_studentfeeledger (
    id bigint NOT NULL,
    created_at timestamp with time zone NOT NULL,
    academic_session_id bigint NOT NULL,
    student_id bigint NOT NULL
);


ALTER TABLE public.finance_studentfeeledger OWNER TO postgres;

--
-- Name: finance_studentfeeledger_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.finance_studentfeeledger ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.finance_studentfeeledger_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: finance_studentfeemonthentry; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.finance_studentfeemonthentry (
    id bigint NOT NULL,
    month integer NOT NULL,
    arrears numeric(10,2) NOT NULL,
    monthly_fee numeric(10,2) NOT NULL,
    exam_fee numeric(10,2) NOT NULL,
    other_charges numeric(10,2) NOT NULL,
    paid_amount numeric(10,2) NOT NULL,
    is_paid boolean NOT NULL,
    last_payment_date date,
    last_receipt_no character varying(50) NOT NULL,
    ledger_id bigint NOT NULL
);


ALTER TABLE public.finance_studentfeemonthentry OWNER TO postgres;

--
-- Name: finance_studentfeemonthentry_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.finance_studentfeemonthentry ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.finance_studentfeemonthentry_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: school_academicsession; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.school_academicsession (
    id bigint NOT NULL,
    name character varying(20) NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    is_active boolean NOT NULL
);


ALTER TABLE public.school_academicsession OWNER TO postgres;

--
-- Name: school_academicsession_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.school_academicsession ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.school_academicsession_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: school_classlevel; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.school_classlevel (
    id bigint NOT NULL,
    name character varying(50) NOT NULL,
    level character varying(20) NOT NULL,
    monthly_fee numeric(10,2) NOT NULL
);


ALTER TABLE public.school_classlevel OWNER TO postgres;

--
-- Name: school_classlevel_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.school_classlevel ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.school_classlevel_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: school_schoolsetting; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.school_schoolsetting (
    id bigint NOT NULL,
    name character varying(255) NOT NULL,
    address text NOT NULL,
    logo character varying(100),
    contact character varying(100) NOT NULL,
    academic_session_format character varying(50) NOT NULL,
    receipt_no_prefix character varying(10) NOT NULL,
    last_receipt_no integer NOT NULL
);


ALTER TABLE public.school_schoolsetting OWNER TO postgres;

--
-- Name: school_schoolsetting_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.school_schoolsetting ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.school_schoolsetting_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: school_section; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.school_section (
    id bigint NOT NULL,
    name character varying(10) NOT NULL,
    class_teacher character varying(255) NOT NULL,
    class_level_id bigint NOT NULL
);


ALTER TABLE public.school_section OWNER TO postgres;

--
-- Name: school_section_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.school_section ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.school_section_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: students_familyhousehold; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.students_familyhousehold (
    id bigint NOT NULL,
    family_id character varying(20) NOT NULL,
    father_guardian_name character varying(255) NOT NULL,
    contact_number character varying(20) NOT NULL,
    address text NOT NULL
);


ALTER TABLE public.students_familyhousehold OWNER TO postgres;

--
-- Name: students_familyhousehold_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.students_familyhousehold ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.students_familyhousehold_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: students_promotionhistory; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.students_promotionhistory (
    id bigint NOT NULL,
    session character varying(20) NOT NULL,
    promotion_date date NOT NULL,
    from_class_id bigint NOT NULL,
    from_section_id bigint NOT NULL,
    to_class_id bigint NOT NULL,
    to_section_id bigint NOT NULL,
    student_id bigint NOT NULL
);


ALTER TABLE public.students_promotionhistory OWNER TO postgres;

--
-- Name: students_promotionhistory_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.students_promotionhistory ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.students_promotionhistory_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: students_student; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.students_student (
    id bigint NOT NULL,
    admission_no character varying(20) NOT NULL,
    admission_date date NOT NULL,
    full_name character varying(255) NOT NULL,
    father_name character varying(255) NOT NULL,
    dob date,
    gender character varying(10) NOT NULL,
    tribe_caste character varying(100) NOT NULL,
    father_occupation character varying(100) NOT NULL,
    residence text NOT NULL,
    contact_number character varying(20) NOT NULL,
    profile_picture character varying(100),
    status character varying(15) NOT NULL,
    inactive_date date,
    remarks text NOT NULL,
    withdrawal_date date,
    class_at_withdrawal character varying(50) NOT NULL,
    arrears_at_withdrawal numeric(10,2) NOT NULL,
    current_class_id bigint NOT NULL,
    current_section_id bigint NOT NULL,
    family_id bigint
);


ALTER TABLE public.students_student OWNER TO postgres;

--
-- Name: students_student_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.students_student ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.students_student_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: teachers_monthlysalarybill; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.teachers_monthlysalarybill (
    id bigint NOT NULL,
    month integer NOT NULL,
    year integer NOT NULL,
    base_pay numeric(10,2) NOT NULL,
    days_present integer NOT NULL,
    allowances numeric(10,2) NOT NULL,
    deductions numeric(10,2) NOT NULL,
    is_paid boolean NOT NULL,
    payment_date date,
    voucher_no character varying(50) NOT NULL,
    teacher_id bigint NOT NULL,
    paid_amount numeric(10,2) NOT NULL
);


ALTER TABLE public.teachers_monthlysalarybill OWNER TO postgres;

--
-- Name: teachers_monthlysalarybill_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.teachers_monthlysalarybill ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.teachers_monthlysalarybill_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: teachers_salaryscale; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.teachers_salaryscale (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    basic_pay numeric(10,2) NOT NULL,
    medical_allowance numeric(10,2) NOT NULL,
    conveyance_allowance numeric(10,2) NOT NULL,
    other_allowances numeric(10,2) NOT NULL
);


ALTER TABLE public.teachers_salaryscale OWNER TO postgres;

--
-- Name: teachers_salaryscale_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.teachers_salaryscale ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.teachers_salaryscale_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: teachers_teacher; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.teachers_teacher (
    id bigint NOT NULL,
    teacher_id character varying(20) NOT NULL,
    full_name character varying(255) NOT NULL,
    father_name character varying(255) NOT NULL,
    cnic character varying(20) NOT NULL,
    dob date,
    qualification text NOT NULL,
    experience text NOT NULL,
    contact_number character varying(20) NOT NULL,
    address text NOT NULL,
    joining_date date NOT NULL,
    designation character varying(100) NOT NULL,
    profile_picture character varying(100),
    status character varying(10) NOT NULL,
    remarks text NOT NULL,
    salary_scale_id bigint
);


ALTER TABLE public.teachers_teacher OWNER TO postgres;

--
-- Name: teachers_teacher_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.teachers_teacher ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.teachers_teacher_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Data for Name: accounts_expense; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.accounts_expense (id, date, category, amount, note, reference, payment_mode) FROM stdin;
1	2026-01-09	Stationery	8200.00	Monthly operational bills & procurement for Stationery	EXP-2026-01-567	Bank
2	2026-01-04	Maintenance	26000.00	Monthly operational bills & procurement for Maintenance	EXP-2026-01-317	Cash
3	2026-01-06	Electricity	28300.00	Monthly operational bills & procurement for Electricity	EXP-2026-01-984	Bank
4	2026-01-12	Other	32400.00	Monthly operational bills & procurement for Other	EXP-2026-01-884	Bank
5	2026-02-02	Stationery	31500.00	Monthly operational bills & procurement for Stationery	EXP-2026-02-309	Cash
6	2026-02-05	Maintenance	31000.00	Monthly operational bills & procurement for Maintenance	EXP-2026-02-471	Cash
7	2026-02-24	Electricity	27500.00	Monthly operational bills & procurement for Electricity	EXP-2026-02-337	Bank
8	2026-02-04	Other	21200.00	Monthly operational bills & procurement for Other	EXP-2026-02-615	Cash
9	2026-03-13	Stationery	22700.00	Monthly operational bills & procurement for Stationery	EXP-2026-03-249	Bank
10	2026-03-09	Maintenance	28300.00	Monthly operational bills & procurement for Maintenance	EXP-2026-03-427	Cash
11	2026-03-14	Electricity	17800.00	Monthly operational bills & procurement for Electricity	EXP-2026-03-234	Cash
12	2026-03-09	Other	8300.00	Monthly operational bills & procurement for Other	EXP-2026-03-703	Bank
13	2026-04-18	Stationery	42300.00	Monthly operational bills & procurement for Stationery	EXP-2026-04-905	Bank
14	2026-04-16	Maintenance	29900.00	Monthly operational bills & procurement for Maintenance	EXP-2026-04-129	Cash
15	2026-04-24	Electricity	30800.00	Monthly operational bills & procurement for Electricity	EXP-2026-04-731	Cash
16	2026-04-08	Other	24100.00	Monthly operational bills & procurement for Other	EXP-2026-04-703	Cash
17	2026-05-06	Stationery	21900.00	Monthly operational bills & procurement for Stationery	EXP-2026-05-501	Cash
18	2026-05-20	Maintenance	10600.00	Monthly operational bills & procurement for Maintenance	EXP-2026-05-616	Cash
19	2026-05-13	Electricity	41600.00	Monthly operational bills & procurement for Electricity	EXP-2026-05-832	Cash
20	2026-05-13	Other	16900.00	Monthly operational bills & procurement for Other	EXP-2026-05-850	Bank
21	2026-06-15	Stationery	30400.00	Monthly operational bills & procurement for Stationery	EXP-2026-06-903	Cash
22	2026-06-22	Maintenance	42900.00	Monthly operational bills & procurement for Maintenance	EXP-2026-06-517	Cash
23	2026-06-18	Electricity	30100.00	Monthly operational bills & procurement for Electricity	EXP-2026-06-262	Cash
24	2026-06-09	Other	14200.00	Monthly operational bills & procurement for Other	EXP-2026-06-645	Cash
25	2026-07-21	Stationery	17600.00	Monthly operational bills & procurement for Stationery	EXP-2026-07-849	Cash
26	2026-07-13	Maintenance	16400.00	Monthly operational bills & procurement for Maintenance	EXP-2026-07-858	Cash
27	2026-07-08	Electricity	36800.00	Monthly operational bills & procurement for Electricity	EXP-2026-07-100	Cash
28	2026-07-01	Other	16400.00	Monthly operational bills & procurement for Other	EXP-2026-07-165	Bank
33	2026-09-04	Other	5600.00	All new and olad party with dues and other cold drinks	2026905	Cash
29	2026-08-02	Stationery	6200.00	Monthly operational bills & procurement for Stationery	EXP-2026-08-872	Cash
30	2026-08-07	Maintenance	7600.00	Monthly operational bills & procurement for Maintenance	EXP-2026-08-256	Bank
31	2026-08-07	Electricity	6300.00	Monthly operational bills & procurement for Electricity	EXP-2026-08-511	Cash
32	2026-08-20	Other	18000.00	Monthly operational bills & procurement for Other	EXP-2026-08-463	Bank
\.


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_group (id, name) FROM stdin;
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can view log entry	1	view_logentry
5	Can add permission	3	add_permission
6	Can change permission	3	change_permission
7	Can delete permission	3	delete_permission
8	Can view permission	3	view_permission
9	Can add group	2	add_group
10	Can change group	2	change_group
11	Can delete group	2	delete_group
12	Can view group	2	view_group
13	Can add user	4	add_user
14	Can change user	4	change_user
15	Can delete user	4	delete_user
16	Can view user	4	view_user
17	Can add content type	5	add_contenttype
18	Can change content type	5	change_contenttype
19	Can delete content type	5	delete_contenttype
20	Can view content type	5	view_contenttype
21	Can add session	6	add_session
22	Can change session	6	change_session
23	Can delete session	6	delete_session
24	Can view session	6	view_session
25	Can add Academic Session	7	add_academicsession
26	Can change Academic Session	7	change_academicsession
27	Can delete Academic Session	7	delete_academicsession
28	Can view Academic Session	7	view_academicsession
29	Can add Class Level	8	add_classlevel
30	Can change Class Level	8	change_classlevel
31	Can delete Class Level	8	delete_classlevel
32	Can view Class Level	8	view_classlevel
33	Can add School Setting	9	add_schoolsetting
34	Can change School Setting	9	change_schoolsetting
35	Can delete School Setting	9	delete_schoolsetting
36	Can view School Setting	9	view_schoolsetting
37	Can add Section	10	add_section
38	Can change Section	10	change_section
39	Can delete Section	10	delete_section
40	Can view Section	10	view_section
41	Can add Family / Household	11	add_familyhousehold
42	Can change Family / Household	11	change_familyhousehold
43	Can delete Family / Household	11	delete_familyhousehold
44	Can view Family / Household	11	view_familyhousehold
45	Can add Student	13	add_student
46	Can change Student	13	change_student
47	Can delete Student	13	delete_student
48	Can view Student	13	view_student
49	Can add Promotion History	12	add_promotionhistory
50	Can change Promotion History	12	change_promotionhistory
51	Can delete Promotion History	12	delete_promotionhistory
52	Can view Promotion History	12	view_promotionhistory
53	Can add Salary Scale	15	add_salaryscale
54	Can change Salary Scale	15	change_salaryscale
55	Can delete Salary Scale	15	delete_salaryscale
56	Can view Salary Scale	15	view_salaryscale
57	Can add Teacher / Staff	16	add_teacher
58	Can change Teacher / Staff	16	change_teacher
59	Can delete Teacher / Staff	16	delete_teacher
60	Can view Teacher / Staff	16	view_teacher
61	Can add Monthly Salary Bill	14	add_monthlysalarybill
62	Can change Monthly Salary Bill	14	change_monthlysalarybill
63	Can delete Monthly Salary Bill	14	delete_monthlysalarybill
64	Can view Monthly Salary Bill	14	view_monthlysalarybill
65	Can add Student Fee Ledger	18	add_studentfeeledger
66	Can change Student Fee Ledger	18	change_studentfeeledger
67	Can delete Student Fee Ledger	18	delete_studentfeeledger
68	Can view Student Fee Ledger	18	view_studentfeeledger
69	Can add Fee Month Entry	19	add_studentfeemonthentry
70	Can change Fee Month Entry	19	change_studentfeemonthentry
71	Can delete Fee Month Entry	19	delete_studentfeemonthentry
72	Can view Fee Month Entry	19	view_studentfeemonthentry
73	Can add Fee Payment Receipt	17	add_feepaymentreceipt
74	Can change Fee Payment Receipt	17	change_feepaymentreceipt
75	Can delete Fee Payment Receipt	17	delete_feepaymentreceipt
76	Can view Fee Payment Receipt	17	view_feepaymentreceipt
77	Can add Expense	20	add_expense
78	Can change Expense	20	change_expense
79	Can delete Expense	20	delete_expense
80	Can view Expense	20	view_expense
81	Can add Exam Mark	23	add_exammark
82	Can change Exam Mark	23	change_exammark
83	Can delete Exam Mark	23	delete_exammark
84	Can view Exam Mark	23	view_exammark
85	Can add Subject	24	add_subject
86	Can change Subject	24	change_subject
87	Can delete Subject	24	delete_subject
88	Can view Subject	24	view_subject
89	Can add Examination	22	add_exam
90	Can change Examination	22	change_exam
91	Can delete Examination	22	delete_exam
92	Can view Examination	22	view_exam
93	Can add Class Subject	21	add_classsubject
94	Can change Class Subject	21	change_classsubject
95	Can delete Class Subject	21	delete_classsubject
96	Can view Class Subject	21	view_classsubject
\.


--
-- Data for Name: auth_user; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) FROM stdin;
2	pbkdf2_sha256$1500000$kMbtaNj6OxVKdcOM4ERu9w$UX3dGbfY1vCTibNFhilY9e/kkPv4E6w0QVgl9MM6HIw=	2026-09-11 18:43:41.046878-07	t	umarsaeed	Umar	Saeed	umarsaeed@kohisar.edu.pk	t	t	2026-09-03 23:36:55-07
1	pbkdf2_sha256$1500000$sYsJ1qoplWjlANfQSkN2OL$jDMmKoH/FbflEZTOV16VzX4uXE3/ggNmvqySINmkvUg=	2026-09-11 20:30:49.01332-07	t	admin	Dr. Farman	Ali	drfarmanali@kohisar.edu.pk	t	t	2026-09-03 22:55:13.883-07
\.


--
-- Data for Name: auth_user_groups; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_user_groups (id, user_id, group_id) FROM stdin;
\.


--
-- Data for Name: auth_user_user_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.auth_user_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
1	2026-09-03 23:36:56.494695-07	2	umarsaeed	1	[{"added": {}}]	4	1
2	2026-09-03 23:37:16.745258-07	2	umarsaeed	2	[{"changed": {"fields": ["First name", "Last name", "Email address", "Staff status", "Superuser status"]}}]	4	1
3	2026-09-06 18:44:09.458082-07	41	REC-1041 - Mustafa Swati (3200.00)	2	[]	17	1
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	group
3	auth	permission
4	auth	user
5	contenttypes	contenttype
6	sessions	session
7	school	academicsession
8	school	classlevel
9	school	schoolsetting
10	school	section
11	students	familyhousehold
12	students	promotionhistory
13	students	student
14	teachers	monthlysalarybill
15	teachers	salaryscale
16	teachers	teacher
17	finance	feepaymentreceipt
18	finance	studentfeeledger
19	finance	studentfeemonthentry
20	accounts	expense
21	exams	classsubject
22	exams	exam
23	exams	exammark
24	exams	subject
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
1	accounts	0001_initial	2026-09-03 22:54:55.833836-07
2	contenttypes	0001_initial	2026-09-03 22:54:55.850875-07
3	auth	0001_initial	2026-09-03 22:54:55.951771-07
4	admin	0001_initial	2026-09-03 22:54:55.984308-07
5	admin	0002_logentry_remove_auto_add	2026-09-03 22:54:55.994978-07
6	admin	0003_logentry_add_action_flag_choices	2026-09-03 22:54:56.013203-07
7	contenttypes	0002_remove_content_type_name	2026-09-03 22:54:56.039802-07
8	auth	0002_alter_permission_name_max_length	2026-09-03 22:54:56.051774-07
9	auth	0003_alter_user_email_max_length	2026-09-03 22:54:56.065253-07
10	auth	0004_alter_user_username_opts	2026-09-03 22:54:56.078248-07
11	auth	0005_alter_user_last_login_null	2026-09-03 22:54:56.089636-07
12	auth	0006_require_contenttypes_0002	2026-09-03 22:54:56.0909-07
13	auth	0007_alter_validators_add_error_messages	2026-09-03 22:54:56.102242-07
14	auth	0008_alter_user_username_max_length	2026-09-03 22:54:56.121147-07
15	auth	0009_alter_user_last_name_max_length	2026-09-03 22:54:56.133666-07
16	auth	0010_alter_group_name_max_length	2026-09-03 22:54:56.14766-07
17	auth	0011_update_proxy_permissions	2026-09-03 22:54:56.160878-07
18	auth	0012_alter_user_first_name_max_length	2026-09-03 22:54:56.170869-07
19	school	0001_initial	2026-09-03 22:54:56.219155-07
20	students	0001_initial	2026-09-03 22:54:56.320124-07
21	finance	0001_initial	2026-09-03 22:54:56.452912-07
22	sessions	0001_initial	2026-09-03 22:54:56.469529-07
23	teachers	0001_initial	2026-09-03 22:54:56.533487-07
24	teachers	0002_monthlysalarybill_paid_amount	2026-09-04 11:57:29.305689-07
25	exams	0001_initial	2026-09-08 19:08:21.360443-07
26	students	0002_alter_student_contact_number_alter_student_dob_and_more	2026-09-08 20:17:30.806829-07
27	teachers	0003_alter_teacher_address_alter_teacher_contact_number_and_more	2026-09-08 20:18:24.028442-07
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
qdza2ipzegh65u8ilpby8c0w0tixzf0b	.eJxVjLsOwjAMAP_FM4rs1AqkIzvfUNlOQgoolfqYEP-OKnWA9e50bxhkW-uwLXkexgQ9eDj9MhV75raL9JB2n5xNbZ1HdXviDru425Ty63q0f4MqS4UeJLJXQuZi2BVF6ugSlMWzZYrGSFiQuoh6ViMpgRNJ0ChZgvpk8PkCzuE3-Q:1x2NaL:xyr344JeWIsqr6vjPtgS3El4j4ChtlzbrRlSOK9zxaM	2026-09-04 02:39:37.896815-07
z2bwq5lydxyv951i92mztw0qvk44iazj	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x2ZHr:bDV9s37FU9xthLwSTzYBguIo1pMHIM8mB-4lGK1CUUY	2026-09-04 15:09:19.68725-07
7ckklprelow2bphbcw8yf4kah2js4nor	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x2Mvq:XzXakCKxnlmeUvmSR1wokincN6680l1P0fah81YOvD8	2026-09-04 01:57:46.791-07
je3p9jprqdxjuveiukwm8gjwsxv3khgv	.eJxVjLsOwjAMAP_FM4rs1AqkIzvfUNlOQgoolfqYEP-OKnWA9e50bxhkW-uwLXkexgQ9eDj9MhV75raL9JB2n5xNbZ1HdXviDru425Ty63q0f4MqS4UeJLJXQuZi2BVF6ugSlMWzZYrGSFiQuoh6ViMpgRNJ0ChZgvpk8PkCzuE3-Q:1x2gQH:UkhKqTUJb_SF_lX5zkQRIKilOfoLhTp1Gz1YIMN3bB0	2026-09-04 22:46:29.131373-07
usi510srptux8nzok9256hy6i05hr4sq	.eJxVjLsOwjAMAP_FM4rs1AqkIzvfUNlOQgoolfqYEP-OKnWA9e50bxhkW-uwLXkexgQ9eDj9MhV75raL9JB2n5xNbZ1HdXviDru425Ty63q0f4MqS4UeJLJXQuZi2BVF6ugSlMWzZYrGSFiQuoh6ViMpgRNJ0ChZgvpk8PkCzuE3-Q:1x2Z0e:1hq0RQAxnhzWGOm_mbcCZk7bSjjIwEV8LYrbltSvU_I	2026-09-04 14:51:32.415758-07
vpq5vmoi1bh99chrxdzxvkhztd6f2930	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x2fQ8:5krBVo8jUlWGFQHZ8q1MbE37hbcDBrLkbSiga4eLBCU	2026-09-04 21:42:16.143846-07
8frs3vgkarff9sfips70nspe07gvc6ew	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x2nek:imt52FSSIoBZcXMzujeo_KmdSsOxi6W0gPaq2p0rbdY	2026-09-05 06:29:54.804386-07
y9sian8in24o4k9iwstede9quqk3625d	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x2ZIP:s73buoPMEHufrtPvg8Q4KgXwZcD3zgNT8PEX-Lg4IA4	2026-09-04 15:09:53.758228-07
8kx33l3qz7uieicxbe28gx08xn2xade0	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x2ZJw:rWW9Xs726-wF0bqAjnvXMxMIwyVLJbEbHjk-rFip5KI	2026-09-04 15:11:28.605325-07
lyob33aeiy9c7863r8h5qnxl90smgmb3	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x2foK:YpLEQJc7_kR4XUNkZYVSHeXqiUxwwj1xZzknVYhzWyo	2026-09-04 22:07:16.711994-07
6czo5u1jmxrowlvv6rs40i9fxcz028hu	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x2fbi:gOEI52GBo9GtsNQzL2U1XxjCyrevaGxl49e2DTHiT-I	2026-09-04 21:54:14.173525-07
wgl2rvvlqc6yrkddkeir3zvnhk3xsvfz	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x2ZK8:bOVGIqorU8RB2deaut0YkxEenMH7ixPtSdhRW125qPk	2026-09-04 15:11:40.849132-07
z01qpf8vyo7c9cbwum3j4njpchhua8zh	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x2Ygo:xPc0zYP3m3nLlxOmXJqVD7gU6hSqtg_DTDwlygyuLKc	2026-09-04 14:31:02.167057-07
1m488munavjkj1sx6ekmz4w9jnw83dsk	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x2fME:Su8-xw80WPRx24OTs8ELzVb5kONHEQlM095hrEqaLiw	2026-09-04 21:38:14.696661-07
kqpe5oylst5i7xsw8uyeeqmmbf61fngp	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x2gOB:m7t205PS_zy5udSrnPmvlodaKuCKDdOncXS_vZpoMgk	2026-09-04 22:44:19.867896-07
norf32iz03rhn8qs1qnb45yyhb8rx9i3	.eJxVjLsOwjAMAP_FM4rs1AqkIzvfUNlOQgoolfqYEP-OKnWA9e50bxhkW-uwLXkexgQ9eDj9MhV75raL9JB2n5xNbZ1HdXviDru425Ty63q0f4MqS4UeJLJXQuZi2BVF6ugSlMWzZYrGSFiQuoh6ViMpgRNJ0ChZgvpk8PkCzuE3-Q:1x2gOi:xjlTwDcQQQhq_WmApaDV91mp3xiM1_VviIRui7xy098	2026-09-04 22:44:52.921637-07
1035zy1y6jk5ghyxt3jmlsxd8bi9aqwc	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x2fO4:JIowUnR_KJ-uld71YPi0zULbd6enNg-iohfTKQxBozQ	2026-09-04 21:40:08.957237-07
cr8em6u7yzaq6xg2s3fm4wczx6stuc3n	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x2fbx:Ef0alotJSScOL8BM_IbntoBGE3LgH4LEeQngpVchXcE	2026-09-04 21:54:29.230791-07
5ptn23360eb9ip7525udb1z8uk6x3o8t	.eJxVjLsOwjAMAP_FM4rs1AqkIzvfUNlOQgoolfqYEP-OKnWA9e50bxhkW-uwLXkexgQ9eDj9MhV75raL9JB2n5xNbZ1HdXviDru425Ty63q0f4MqS4UeJLJXQuZi2BVF6ugSlMWzZYrGSFiQuoh6ViMpgRNJ0ChZgvpk8PkCzuE3-Q:1x2NYn:xMjHUtaZJTVBlVtvcOCaGtqMTHjfntd1B-sVHzsh44w	2026-09-04 02:38:01.325735-07
3io9ntjgtljohcrxsdw2fhozbm66pb1k	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x2ZHF:7uv208Vnndecyu7JbSJxW_eOzbnchiNlX675NR-1vAg	2026-09-04 15:08:41.771146-07
gstt76wf4q3r1bzi0t4euh88509tesr7	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x2fP1:pbSz4LYqpG7mqVZs1OSyDBI2L2NWOFo9yNfdMBu9DZ4	2026-09-04 21:41:07.060355-07
0wqwtvghd89c13lx1l7n6l76fwy3vjba	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x2feO:rOYYB1RypK8GtegvXqznA4x_cA__fH5575WmOkwLczM	2026-09-04 21:57:00.408759-07
cuzz6va9vbadgbg1tqsvigg3fvx1ii9t	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x2fPH:QlkEt7ilcY-g4wsA3UYiMFtdlTJXQd09Xkf5avgi2bo	2026-09-04 21:41:23.481343-07
rwiqg1akrrumur8hvlw8ufa022jknl3s	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x2fef:ZjRMrGF3Yefe7g65R_1ItZs0TYfMzRRD9yRqP7BE05Q	2026-09-04 21:57:17.719855-07
ebsnlwliyjechwycrn1t6r8xv3gihb4q	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x2Mug:os_YHXJW5eaOktlt7v54s0moCSM6nPhsc_Nx3U1br94	2026-09-04 01:56:34.544-07
wifcgmclwx45l7q43qv5iab2jl8vzh3u	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x2N0e:wRapy3JRW4CNA5w3cEG0No-m9VD4qWivbcc5Qicd0pk	2026-09-04 02:02:44.081-07
2625u32lcf9lqha5hlfcw8q0vckpwksq	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x47ql:pEyZCv-HQzLMMnQCmWFda5Ns7Cjt2cByAiplHc7b7oA	2026-09-08 22:15:47.052714-07
jbchm46aqbfb1phgewekrdnstkcee6wk	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x48Zg:nqsvYg_e8WBaA6mMMh5Hyba5YfRUvsTeqdd1K32wXMc	2026-09-08 23:02:12.900229-07
gb5dit08x9cmj0zkaa1qt2qa7m2a0e7s	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x2fpB:AeyA362lf3Gb5Dwb1b9W1EsXeyhwFD1-RTT7hdzNRn0	2026-09-04 22:08:09.420338-07
w25x2ao4a66j6zggvc6m5lpjfdpoqeuw	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x485R:DK1U7tJljImXhFrrZhCGAk_Z4htJHCEx61qtJyoUjB8	2026-09-08 22:30:57.527462-07
cfd3aqa5mcsp7kfknkttt41v558k073w	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x5D01:tqH4M7wL7NEeUaRePZjRgCvAMl9qYjIO_e0KGt3Qdic	2026-09-11 21:57:49.466731-07
fvzxqab7sr336p18v0a7rbzbczajo6ag	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x4qUb:Mb-l-CTSTZfYNJ2ybrq65JZ79KhvPR8hH4gnpvU3RfM	2026-09-10 21:55:53.950924-07
27axf9e2w3gznii4qhd0e32glbwm5pzk	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x4qa5:BKTIencCo9U8cLXrn7qo6CFIYVKKE6y_j-U9JrFNMPk	2026-09-10 22:01:33.710395-07
ncf6kg7o3a3b0qe8od4bujd1e9eaf8cw	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x48KK:EpLQz2CRjn8V2c3cEuc9wFLQfwkUMFqEweLnt3srH2M	2026-09-08 22:46:20.907788-07
1w18s5xkdzajo76au9808sxaaqkfv5d7	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x2gOP:3V-3U-ij_FJetRZ8uTytNkRjZ0ii5rtY_T9bm3lEyWs	2026-09-04 22:44:33.418561-07
wpe2iom06tlov15xxsg9fiu035rk6aoj	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x48Go:n_iLZ9fQgvJ5NxKi0WvhmMI11GKrhdh7c00zguzA8_c	2026-09-08 22:42:42.429782-07
vv3nalgno37vf7x5z8lf9fweha213iq0	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x4E7x:QWP7JDU26eyOe4na703Z-Qu3_smcAKdvb3_uvZQSQr4	2026-09-09 04:57:57.763938-07
l53eveqecnn9tw149a85ktiif9lsxgwy	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x4qUQ:j-I_-Mk2wxTlbLZAVaY_xNZD3lKtECR-pJK7R683q64	2026-09-10 21:55:42.881621-07
s8sf8xrtjh2ixdzvnqg3ki6tmlwy7qew	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x5Ctc:XjiMeRjIUxSVtAGfFL5pJfOi2vKTkg4GOVc6tSmbAIo	2026-09-11 21:51:12.371715-07
0lu2b08lp23be8n32idvm0xo94cdxdq2	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x3OTA:XgOdUzv93WlnrsTWBSLSppGgVThN0aeg1pWv__msWSI	2026-09-06 21:48:24.758545-07
dzqft5yrceqdizwxtiuxeuv3grhrpke6	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x47qY:DJOw5RvseYZLipaqU_lrn8tAwdUJHvJJlm5GOxMyRAo	2026-09-08 22:15:34.274418-07
rs8mw1g06nnzq54v9zysg46ten55rznq	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x5E33:fbOurC1s2b1ke_6VbDQfkq5YpXrrDbtyx0KsQwQFSqo	2026-09-11 23:05:01.877503-07
k66arh5gllt5p5l7bafi2nnmrj4ailse	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x5ES1:yjWwsG-6CDHIc0AIIed-PtK3jYueAPW5kTIBnNvUsNM	2026-09-11 23:30:49.743169-07
1320l0q23egb5b6j9c5v0m0sa0kr7wi8	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x2fpM:5753JiAHCZO1wshFB4vneMGw19KJnaS9T6FjiOWk6Jg	2026-09-04 22:08:20.464369-07
w6z8v672yjcsz8nrfyim9sk2oqu0a665	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x2gKg:ppg2112Kd335Pg5Kjp1OXDvgUh6rbH5zJoQ8x_-1yFg	2026-09-04 22:40:42.070782-07
7vl8nxc7um0l5cs9d3jslxktci8hovof	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x485i:Dz1YdZ9pHEx8PlNoBG6JBRmO9gN93nHWejFg7BtWjPg	2026-09-08 22:31:14.323666-07
psme3m699usqa42t5wdycpioh1idowg5	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x48Oa:H-An5imGtUMYGZ7TSBOA8KoYNTg3d8BXcppEeE36QNI	2026-09-08 22:50:44.050482-07
y3nq4fvpxvv8rjf119tson0z9885ap5c	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x48aC:W_iyrGMl6WVQ4Z-XyujJIFD0B5Um-nUWrLQ16BbaSpc	2026-09-08 23:02:44.912799-07
7zmrk41l91mqdv1yjkpqamzis0562gjw	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x4qVS:WPbEN-19OZE2XZX0lzUSwF-f-6qcXF_ZigRnXTlI5X0	2026-09-10 21:56:46.469473-07
tkgwpblrte0kjl0c86mqqgrdvkylbf3w	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x2gOb:bAE341_Y-TYY-E-FCciPgzzxT9oT0Jd3nPg0xKdQRTo	2026-09-04 22:44:45.576877-07
2k7p0wm5s6tvm7wnxlz63mobq71uirbq	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x48HT:amMkGtq_MOw6CJd4qCKV6L7u_tKgzDthgRPmZSdzeFw	2026-09-08 22:43:23.72518-07
9t6bhtzchjsgfasj2rvl7rner6wjqu22	.eJxVjLsOwjAMAP_FM4rs1AqkIzvfUNlOQgoolfqYEP-OKnWA9e50bxhkW-uwLXkexgQ9eDj9MhV75raL9JB2n5xNbZ1HdXviDru425Ty63q0f4MqS4UeJLJXQuZi2BVF6ugSlMWzZYrGSFiQuoh6ViMpgRNJ0ChZgvpk8PkCzuE3-Q:1x5EZE:FW6HcPUiOgi0oEDFllbWuQjKkl5bYmylrf3XCEugMA8	2026-09-11 23:38:16.468112-07
y7i53ipvn3ol7kx7wt1u2407vwlf7cab	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x5D0M:NpsPy84UmvbFJyh7XcNUppFi6kQC9LBhUmSO-dfNU6o	2026-09-11 21:58:10.731731-07
y5gjud2l19ij5aeiyk3z585pwsa651a1	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x47l5:mlQZNQw50H7foRWddHzPPqsM_HVPkSgVyxdeKFyzJ5g	2026-09-08 22:09:55.896392-07
kvm3iq3an2dfw3ij10ut7u7bzdast9cm	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x4qd9:F3TB9Bar6jYwvD-JLnoFCh5LAcUJ4jOdWbSeMMlrdqY	2026-09-10 22:04:43.425997-07
5ylymlznwqyow2429izra2wum64kmaxd	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x4qen:VnQVOVjMwCenJHJWOQhLWmwI6xA8zvVkRuNgIhgTXhQ	2026-09-10 22:06:25.700319-07
el9xcx1amaikow5x6unjrgeypok3w3ty	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x2gOr:JDl8BOKp6vA3VndXBL7JL96ZFopOOWxHDgadaLpVqo4	2026-09-04 22:45:01.587866-07
yeof3h8166dz6hh27osglbphfxnlk2hv	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x2gL5:PQXmGrje8WdXn8AYe2G9uO-BfABpprDat4wvtKJsEyQ	2026-09-04 22:41:07.078674-07
9y846ifbjnppfk72mbcyhgeqt5bjg5pw	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x4qZY:6_BUYrAEMkYwKOe-tL5SVem41V2KHno0GOQLXA2uMSY	2026-09-10 22:01:00.489485-07
dk3nohh28oxddmv8echiszgdhqdmayyh	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x2fpZ:SRgK8dONHc3VbdFMqgGufTeGmOwVRc9CgX2xfCPG5CI	2026-09-04 22:08:33.402828-07
55y44h07zk85w45dblim86r001u3spxd	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x5CtJ:v-mKG3VUujkLOD6Dd2YZYkGrBjuzKI4NeahN4mDboNg	2026-09-11 21:50:53.258996-07
gqj0ndip9b5h7unqbftg7zstwrns3xpb	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x5ERh:rkVhLtIKNXEFFRWGmr3QzOiWfD9ftwHKgMpI2uRJ350	2026-09-11 23:30:29.302798-07
pq6cc1a1562t8rc8wvq0p2i2l4wgbx2a	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x4yZf:Nh01Zg22qcOalZdfhazn7fsKfUxrsrBIPXVdHNugaoc	2026-09-11 06:33:39.221143-07
priudnpf392bx143wf6kzx62k9eoqudp	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x4882:FmyuAJdFoRAtEuxH-KSQBAFO-xBkBKlqEplIWWKiJMg	2026-09-08 22:33:38.799937-07
jnp0jzb3kn00wbuce7sv7v8btt5v56vh	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x48Ok:aIIQY8-ab_QNboo3LNqD4rfGsy5pC7vIfUizPofJIbk	2026-09-08 22:50:54.668015-07
0qsvwrepq98amte3uop7pcm8goztyw92	.eJxVjLsOwjAMAP_FM4rs1AqkIzvfUNlOQgoolfqYEP-OKnWA9e50bxhkW-uwLXkexgQ9eDj9MhV75raL9JB2n5xNbZ1HdXviDru425Ty63q0f4MqS4UeJLJXQuZi2BVF6ugSlMWzZYrGSFiQuoh6ViMpgRNJ0ChZgvpk8PkCzuE3-Q:1x48rL:Dl5Jh0ztA0U-gS6_uZFuTfJv0SmON9EFemgfZ0Jrxoo	2026-09-08 23:20:27.379102-07
gpo171vilxaq2gu084e68wk1ptooxdu3	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x4qUA:yh8rZoJteUw4WOo26K9Js__IYQiqN43UJrbcBkNIcaE	2026-09-10 21:55:26.160629-07
cqybmz4sfr4rp7u7hin815my0zgst13e	.eJxVjDEOwjAMAP_iGUUpoU7SkZ03VHbskAJKpaadEH9HlTrAene6N4y0rWXcmi7jJDBAB6dfxpSeWnchD6r32aS5rsvEZk_MYZu5zaKv69H-DQq1AgOo9c56n7oUc4q5z5G7yDb3HJjECmJwhEp0ZutUUFMIXhE9BmLJF_h8Afz0ONU:1x48fZ:ejiQLd1iENyNkJubSIInFpZGs9pW7SeCZ-5yo-jv2q4	2026-09-08 23:08:17.056257-07
\.


--
-- Data for Name: exams_classsubject; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exams_classsubject (id, total_marks, passing_marks, "order", class_level_id, subject_id) FROM stdin;
10	75.0	25.0	1	13	1
11	75.0	25.0	2	13	2
12	75.0	25.0	3	13	3
13	75.0	25.0	4	13	4
14	50.0	17.0	5	13	5
15	75.0	25.0	6	13	6
16	75.0	25.0	7	13	7
17	75.0	25.0	8	13	8
18	50.0	17.0	9	13	9
19	75.0	25.0	1	16	1
20	75.0	25.0	2	16	2
21	75.0	25.0	3	16	3
22	75.0	25.0	4	16	4
23	50.0	17.0	5	16	5
24	75.0	25.0	6	16	6
25	75.0	25.0	7	16	7
26	75.0	25.0	8	16	8
27	50.0	17.0	9	16	9
28	75.0	25.0	1	14	1
29	75.0	25.0	2	14	2
30	75.0	25.0	3	14	3
31	75.0	25.0	4	14	4
32	50.0	17.0	5	14	5
33	75.0	25.0	6	14	6
34	75.0	25.0	7	14	7
35	75.0	25.0	8	14	8
36	50.0	17.0	9	14	9
37	100.0	33.0	1	3	1
38	100.0	33.0	2	3	2
39	100.0	33.0	3	3	3
40	100.0	33.0	4	3	11
41	50.0	17.0	5	3	5
42	50.0	17.0	6	3	4
43	50.0	17.0	7	3	9
44	50.0	17.0	8	3	12
45	75.0	25.0	1	12	1
46	75.0	25.0	2	12	2
47	75.0	25.0	3	12	3
48	75.0	25.0	4	12	4
49	50.0	17.0	5	12	5
50	75.0	25.0	6	12	6
51	75.0	25.0	7	12	7
52	75.0	25.0	8	12	8
53	50.0	17.0	9	12	9
54	100.0	33.0	1	4	1
55	100.0	33.0	2	4	2
56	100.0	33.0	3	4	3
57	100.0	33.0	4	4	11
58	50.0	17.0	5	4	5
59	50.0	17.0	6	4	4
60	50.0	17.0	7	4	9
61	50.0	17.0	8	4	12
62	100.0	33.0	1	5	1
63	100.0	33.0	2	5	2
64	100.0	33.0	3	5	3
65	100.0	33.0	4	5	11
66	50.0	17.0	5	5	5
67	50.0	17.0	6	5	4
68	50.0	17.0	7	5	9
69	50.0	17.0	8	5	12
70	100.0	33.0	1	6	1
71	100.0	33.0	2	6	2
72	100.0	33.0	3	6	3
73	100.0	33.0	4	6	11
74	50.0	17.0	5	6	5
75	50.0	17.0	6	6	4
76	50.0	17.0	7	6	9
77	50.0	17.0	8	6	12
78	100.0	33.0	1	7	1
79	100.0	33.0	2	7	2
80	100.0	33.0	3	7	3
81	100.0	33.0	4	7	11
82	50.0	17.0	5	7	5
83	50.0	17.0	6	7	4
84	50.0	17.0	7	7	9
85	50.0	17.0	8	7	12
86	100.0	33.0	1	8	1
87	100.0	33.0	2	8	2
88	100.0	33.0	3	8	3
89	100.0	33.0	4	8	11
90	50.0	17.0	5	8	5
91	50.0	17.0	6	8	4
92	50.0	17.0	7	8	9
93	50.0	17.0	8	8	12
94	100.0	33.0	1	9	1
95	100.0	33.0	2	9	2
96	100.0	33.0	3	9	3
97	100.0	33.0	4	9	11
98	50.0	17.0	5	9	5
99	50.0	17.0	6	9	4
100	50.0	17.0	7	9	9
101	50.0	17.0	8	9	12
102	100.0	33.0	1	10	1
103	100.0	33.0	2	10	2
104	100.0	33.0	3	10	3
105	100.0	33.0	4	10	11
106	50.0	17.0	5	10	5
107	50.0	17.0	6	10	4
108	50.0	17.0	7	10	9
109	50.0	17.0	8	10	12
110	75.0	25.0	1	11	1
111	75.0	25.0	2	11	2
112	75.0	25.0	3	11	3
113	75.0	25.0	4	11	4
114	50.0	17.0	5	11	5
115	75.0	25.0	6	11	6
116	75.0	25.0	7	11	7
117	75.0	25.0	8	11	8
118	50.0	17.0	9	11	9
119	75.0	25.0	1	17	1
120	75.0	25.0	2	17	2
3	75.0	25.0	3	15	3
5	50.0	17.0	5	15	5
6	75.0	25.0	6	15	6
7	75.0	25.0	7	15	7
8	75.0	25.0	8	15	8
9	50.0	17.0	9	15	9
2	75.0	25.0	2	15	2
121	75.0	25.0	3	17	3
122	75.0	25.0	4	17	4
123	50.0	17.0	5	17	5
124	75.0	25.0	6	17	6
125	75.0	25.0	7	17	7
126	75.0	25.0	8	17	8
127	50.0	17.0	9	17	9
128	75.0	25.0	1	18	1
129	75.0	25.0	2	18	2
130	75.0	25.0	3	18	3
131	75.0	25.0	4	18	4
132	50.0	17.0	5	18	5
133	75.0	25.0	6	18	6
134	75.0	25.0	7	18	7
135	75.0	25.0	8	18	8
136	50.0	17.0	9	18	9
137	100.0	33.0	1	1	1
138	100.0	33.0	2	1	2
139	100.0	33.0	3	1	3
140	50.0	17.0	4	1	14
141	50.0	17.0	5	1	15
142	50.0	17.0	6	1	13
143	100.0	33.0	1	2	1
144	100.0	33.0	2	2	2
145	100.0	33.0	3	2	3
146	50.0	17.0	4	2	14
147	50.0	17.0	5	2	15
148	50.0	17.0	6	2	13
1	75.0	25.0	1	15	1
\.


--
-- Data for Name: exams_exam; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exams_exam (id, name, start_date, end_date, is_active, created_at, session_id) FROM stdin;
1	First Term Examination 2026	\N	\N	t	2026-09-08 19:11:56.62528-07	2
2	Annual Examination 2026	\N	\N	f	2026-09-08 19:11:56.63235-07	2
3	Mid Term Exam	2026-09-12	2026-09-30	t	2026-09-08 19:19:17.608429-07	2
\.


--
-- Data for Name: exams_exammark; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exams_exammark (id, total_marks, obtained_marks, is_absent, remarks, updated_at, class_level_id, exam_id, student_id, subject_id) FROM stdin;
2	75.0	32.0	f		2026-09-08 19:12:22.868128-07	11	1	11	2
3	75.0	26.0	f		2026-09-08 19:12:22.872476-07	11	1	11	3
4	75.0	72.0	f		2026-09-08 19:12:22.877119-07	11	1	11	4
5	50.0	34.0	f		2026-09-08 19:12:22.882927-07	11	1	11	5
6	75.0	40.0	f		2026-09-08 19:12:22.888552-07	11	1	11	6
7	75.0	39.0	f		2026-09-08 19:12:22.89419-07	11	1	11	7
8	75.0	33.0	f		2026-09-08 19:12:22.901176-07	11	1	11	8
9	50.0	23.0	f		2026-09-08 19:12:22.906561-07	11	1	11	9
11	75.0	72.0	f		2026-09-08 19:12:22.914401-07	11	1	29	2
12	75.0	59.0	f		2026-09-08 19:12:22.919626-07	11	1	29	3
13	75.0	30.0	f		2026-09-08 19:12:22.924183-07	11	1	29	4
14	50.0	44.0	f		2026-09-08 19:12:22.928759-07	11	1	29	5
15	75.0	27.0	f		2026-09-08 19:12:22.935238-07	11	1	29	6
16	75.0	26.0	f		2026-09-08 19:12:22.938609-07	11	1	29	7
17	75.0	30.0	f		2026-09-08 19:12:22.941857-07	11	1	29	8
18	50.0	30.0	f		2026-09-08 19:12:22.945005-07	11	1	29	9
20	75.0	57.0	f		2026-09-08 19:12:22.954093-07	11	1	47	2
21	75.0	63.0	f		2026-09-08 19:12:22.957825-07	11	1	47	3
22	75.0	26.0	f		2026-09-08 19:12:22.961023-07	11	1	47	4
23	50.0	29.0	f		2026-09-08 19:12:22.965298-07	11	1	47	5
24	75.0	70.0	f		2026-09-08 19:12:22.969297-07	11	1	47	6
25	75.0	66.0	f		2026-09-08 19:12:22.972626-07	11	1	47	7
26	75.0	69.0	f		2026-09-08 19:12:22.975804-07	11	1	47	8
27	50.0	43.0	f		2026-09-08 19:12:22.978972-07	11	1	47	9
29	75.0	53.0	f		2026-09-08 19:12:22.987336-07	11	1	65	2
30	75.0	62.0	f		2026-09-08 19:12:22.991018-07	11	1	65	3
31	75.0	42.0	f		2026-09-08 19:12:22.994206-07	11	1	65	4
32	50.0	17.0	f		2026-09-08 19:12:22.998412-07	11	1	65	5
33	75.0	73.0	f		2026-09-08 19:12:23.002724-07	11	1	65	6
34	75.0	35.0	f		2026-09-08 19:12:23.005834-07	11	1	65	7
35	75.0	69.0	f		2026-09-08 19:12:23.008992-07	11	1	65	8
36	50.0	44.0	f		2026-09-08 19:12:23.012007-07	11	1	65	9
60	75.0	34.0	f		2026-09-11 18:46:39.409687-07	15	3	33	6
49	75.0	55.0	f		2026-09-11 18:46:39.350924-07	15	3	15	2
50	75.0	55.0	f		2026-09-11 18:46:39.360197-07	15	3	15	3
51	50.0	34.0	f		2026-09-11 18:46:39.363401-07	15	3	15	5
52	75.0	47.0	f		2026-09-11 18:46:39.366795-07	15	3	15	6
53	75.0	34.0	f		2026-09-11 18:46:39.374417-07	15	3	15	7
1	75.0	71.0	f		2026-09-08 19:15:20.654559-07	11	1	11	1
10	75.0	0.0	t		2026-09-08 19:15:20.657506-07	11	1	29	1
19	75.0	39.0	f		2026-09-08 19:15:20.659788-07	11	1	47	1
28	75.0	39.0	f		2026-09-08 19:15:20.662386-07	11	1	65	1
54	75.0	44.0	f		2026-09-11 18:46:39.377928-07	15	3	15	8
46	100.0	85.0	f		2026-09-08 19:31:14.290693-07	9	3	9	1
47	100.0	90.0	f		2026-09-08 19:31:14.293716-07	9	3	9	2
55	50.0	23.0	f		2026-09-11 18:46:39.381062-07	15	3	15	9
57	75.0	44.0	f		2026-09-11 18:46:39.392099-07	15	3	33	2
58	75.0	34.0	f		2026-09-11 18:46:39.396899-07	15	3	33	3
59	50.0	34.0	f		2026-09-11 18:46:39.401496-07	15	3	33	5
61	75.0	44.0	f		2026-09-11 18:46:39.414039-07	15	3	33	7
62	75.0	44.0	f		2026-09-11 18:46:39.417813-07	15	3	33	8
63	50.0	44.0	f		2026-09-11 18:46:39.425753-07	15	3	33	9
65	75.0	34.0	f		2026-09-11 18:46:39.43212-07	15	3	51	2
66	75.0	34.0	f		2026-09-11 18:46:39.435791-07	15	3	51	3
67	50.0	34.0	f		2026-09-11 18:46:39.441468-07	15	3	51	5
68	75.0	34.0	f		2026-09-11 18:46:39.444846-07	15	3	51	6
69	75.0	34.0	f		2026-09-11 18:46:39.447762-07	15	3	51	7
70	75.0	34.0	f		2026-09-11 18:46:39.451121-07	15	3	51	8
48	75.0	44.0	f		2026-09-11 18:46:39.346898-07	15	3	15	1
56	75.0	55.0	f		2026-09-11 18:46:39.38425-07	15	3	33	1
64	75.0	56.0	f		2026-09-11 18:46:39.429128-07	15	3	51	1
71	50.0	24.0	f		2026-09-11 18:46:39.457282-07	15	3	51	9
72	75.0	67.0	f		2026-09-11 18:46:39.473412-07	15	3	69	1
73	75.0	34.0	f		2026-09-11 18:46:39.477177-07	15	3	69	2
74	75.0	43.0	f		2026-09-11 18:46:39.480199-07	15	3	69	3
75	50.0	34.0	f		2026-09-11 18:46:39.483478-07	15	3	69	5
76	75.0	44.0	f		2026-09-11 18:46:39.489346-07	15	3	69	6
77	75.0	34.0	f		2026-09-11 18:46:39.492664-07	15	3	69	7
78	75.0	34.0	f		2026-09-11 18:46:39.496224-07	15	3	69	8
79	50.0	34.0	f		2026-09-11 18:46:39.499506-07	15	3	69	9
156	50.0	33.0	f		2026-09-11 18:46:39.515459-07	15	3	160	5
157	75.0	23.0	f		2026-09-11 18:46:39.527795-07	15	3	160	6
158	75.0	24.0	f		2026-09-11 18:46:39.531292-07	15	3	160	7
159	75.0	44.0	f		2026-09-11 18:46:39.534887-07	15	3	160	8
112	100.0	44.0	f		2026-09-08 20:19:39.377503-07	1	3	1	1
113	100.0	44.0	f		2026-09-08 20:19:39.38193-07	1	3	1	2
114	100.0	44.0	f		2026-09-08 20:19:39.385668-07	1	3	1	3
115	50.0	44.0	f		2026-09-08 20:19:39.389781-07	1	3	1	14
116	50.0	44.0	f		2026-09-08 20:19:39.39456-07	1	3	1	15
117	50.0	44.0	f		2026-09-08 20:19:39.398654-07	1	3	1	13
118	100.0	44.0	f		2026-09-08 20:19:39.403012-07	1	3	19	1
119	100.0	44.0	f		2026-09-08 20:19:39.407517-07	1	3	19	2
120	100.0	44.0	f		2026-09-08 20:19:39.411567-07	1	3	19	3
121	50.0	44.0	f		2026-09-08 20:19:39.415954-07	1	3	19	14
122	50.0	44.0	f		2026-09-08 20:19:39.420226-07	1	3	19	15
123	50.0	44.0	f		2026-09-08 20:19:39.42464-07	1	3	19	13
124	100.0	44.0	f		2026-09-08 20:19:39.429809-07	1	3	37	1
125	100.0	44.0	f		2026-09-08 20:19:39.434266-07	1	3	37	2
126	100.0	44.0	f		2026-09-08 20:19:39.438652-07	1	3	37	3
127	50.0	44.0	f		2026-09-08 20:19:39.443178-07	1	3	37	14
128	50.0	44.0	f		2026-09-08 20:19:39.447988-07	1	3	37	15
129	50.0	44.0	f		2026-09-08 20:19:39.452423-07	1	3	37	13
130	100.0	44.0	f		2026-09-08 20:19:39.456036-07	1	3	55	1
131	100.0	44.0	f		2026-09-08 20:19:39.46068-07	1	3	55	2
132	100.0	44.0	f		2026-09-08 20:19:39.465851-07	1	3	55	3
133	50.0	44.0	f		2026-09-08 20:19:39.470724-07	1	3	55	14
134	50.0	44.0	f		2026-09-08 20:19:39.475289-07	1	3	55	15
135	50.0	44.0	f		2026-09-08 20:19:39.479324-07	1	3	55	13
160	50.0	50.0	f		2026-09-11 18:46:39.539537-07	15	3	160	9
154	75.0	55.0	f		2026-09-11 18:46:39.542786-07	15	3	162	1
155	75.0	60.0	f		2026-09-11 18:46:39.547954-07	15	3	162	2
142	75.0	65.0	f		2026-09-11 18:46:39.505435-07	15	3	160	1
143	75.0	70.0	f		2026-09-11 18:46:39.508513-07	15	3	160	2
148	100.0	55.0	f		2026-09-08 20:19:42.114131-07	1	3	161	1
149	100.0	45.0	f		2026-09-08 20:19:42.118504-07	1	3	161	2
150	100.0	55.0	f		2026-09-08 20:19:42.12318-07	1	3	161	3
144	75.0	72.0	f		2026-09-11 18:46:39.512034-07	15	3	160	3
145	50.0	44.0	f		2026-09-08 20:19:40.83857-07	1	3	160	14
146	50.0	44.0	f		2026-09-08 20:19:40.842837-07	1	3	160	15
147	50.0	44.0	f		2026-09-08 20:19:40.846742-07	1	3	160	13
151	50.0	50.0	f		2026-09-08 20:19:42.127768-07	1	3	161	14
152	50.0	45.0	f		2026-09-08 20:19:42.133323-07	1	3	161	15
153	50.0	44.0	f		2026-09-08 20:19:42.136949-07	1	3	161	13
136	100.0	44.0	f		2026-09-08 20:19:44.785497-07	1	3	73	1
137	100.0	44.0	f		2026-09-08 20:19:44.792451-07	1	3	73	2
138	100.0	44.0	f		2026-09-08 20:19:44.797808-07	1	3	73	3
139	50.0	44.0	f		2026-09-08 20:19:44.803165-07	1	3	73	14
140	50.0	44.0	f		2026-09-08 20:19:44.808801-07	1	3	73	15
141	50.0	44.0	f		2026-09-08 20:19:44.814279-07	1	3	73	13
\.


--
-- Data for Name: exams_subject; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exams_subject (id, name, code, "order", is_active) FROM stdin;
1	English	Eng	1	t
2	Urdu	Urdu	2	t
3	Mathematics	Maths	3	t
4	Pakistan Studies	P.Study	4	t
5	Islamyat	Islamyat	5	t
6	Biology	Bio	6	t
7	Chemistry	Che	7	t
8	Physics	Phy	8	t
9	Mutalae Quran	M.quran	9	t
10	Computer Science	CS	10	t
11	General Science	G.Sci	11	t
12	Pashto	Pashto	12	t
13	Drawing / Art	Drawing	13	t
14	General Knowledge	GK	14	t
15	Nazra Quran	Nazra	15	t
16	Arabic Language 2	ARb2	10	t
\.


--
-- Data for Name: finance_feepaymentreceipt; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.finance_feepaymentreceipt (id, receipt_no, payment_date, amount_paid, remarks, student_id) FROM stdin;
51	REC-1051	2026-09-04	19500.00	he /just pay	69
53	REC-1053	2026-09-04	6000.00		1
55	REC-1055	2026-09-05	2300.00		1
1	REC-1001	2026-05-22	7500.00	Cash payment cleared at accounts counter	1
2	REC-1002	2026-08-17	2800.00	Cash payment cleared at accounts counter	2
3	REC-1003	2026-04-23	9000.00	Cash payment cleared at accounts counter	3
4	REC-1004	2026-03-09	3000.00	Cash payment cleared at accounts counter	4
5	REC-1005	2026-03-21	19200.00	Cash payment cleared at accounts counter	5
6	REC-1006	2026-08-28	3200.00	Cash payment cleared at accounts counter	6
7	REC-1007	2026-03-02	3500.00	Cash payment cleared at accounts counter	7
8	REC-1008	2026-05-03	11400.00	Cash payment cleared at accounts counter	8
9	REC-1009	2026-01-26	4000.00	Cash payment cleared at accounts counter	9
10	REC-1010	2026-07-18	25200.00	Cash payment cleared at accounts counter	10
11	REC-1011	2026-03-10	14400.00	Cash payment cleared at accounts counter	11
12	REC-1012	2026-07-20	5000.00	Cash payment cleared at accounts counter	12
13	REC-1013	2026-02-11	39000.00	Cash payment cleared at accounts counter	13
14	REC-1014	2026-01-22	6800.00	Cash payment cleared at accounts counter	14
15	REC-1015	2026-02-21	19500.00	Cash payment cleared at accounts counter	15
17	REC-1017	2026-07-16	36000.00	Cash payment cleared at accounts counter	17
18	REC-1018	2026-07-15	6200.00	Cash payment cleared at accounts counter	18
19	REC-1019	2026-06-09	15000.00	Cash payment cleared at accounts counter	19
20	REC-1020	2026-08-14	8400.00	Cash payment cleared at accounts counter	20
21	REC-1021	2026-08-16	9000.00	Cash payment cleared at accounts counter	21
22	REC-1022	2026-04-22	3000.00	Cash payment cleared at accounts counter	22
23	REC-1023	2026-05-11	19200.00	Cash payment cleared at accounts counter	23
24	REC-1024	2026-06-22	19200.00	Cash payment cleared at accounts counter	24
25	REC-1025	2026-06-21	3500.00	Cash payment cleared at accounts counter	25
58	REC-1056	2026-09-05	40000.00	Family Payment: FAM-0019 (Sardar Jan).	19
59	REC-1057	2026-09-09	1200.00		8
16	REC-1016	2026-01-03	40800.00	Cash payment cleared at accounts counter	16
42	REC-1042	2026-01-02	9600.00	Cash payment cleared at accounts counter	42
43	REC-1043	2026-02-15	10500.00	Cash payment cleared at accounts counter	43
44	REC-1044	2026-07-12	3800.00	Cash payment cleared at accounts counter	44
45	REC-1045	2026-07-02	12000.00	Cash payment cleared at accounts counter	45
46	REC-1046	2026-02-05	4200.00	Cash payment cleared at accounts counter	46
47	REC-1047	2026-06-21	14400.00	Cash payment cleared at accounts counter	47
48	REC-1048	2026-06-04	15000.00	Cash payment cleared at accounts counter	48
52	REC-1052	2026-09-04	2300.00		57
54	REC-1054	2026-09-04	2800.00		2
26	REC-1026	2026-04-27	3800.00	Cash payment cleared at accounts counter	26
27	REC-1027	2026-08-10	12000.00	Cash payment cleared at accounts counter	27
28	REC-1028	2026-01-11	25200.00	Cash payment cleared at accounts counter	28
29	REC-1029	2026-06-22	14400.00	Cash payment cleared at accounts counter	29
30	REC-1030	2026-02-20	5000.00	Cash payment cleared at accounts counter	30
31	REC-1031	2026-08-24	19500.00	Cash payment cleared at accounts counter	31
32	REC-1032	2026-07-17	40800.00	Cash payment cleared at accounts counter	32
33	REC-1033	2026-08-28	19500.00	Cash payment cleared at accounts counter	33
34	REC-1034	2026-05-25	40800.00	Cash payment cleared at accounts counter	34
35	REC-1035	2026-03-27	6000.00	Cash payment cleared at accounts counter	35
36	REC-1036	2026-04-01	18600.00	Cash payment cleared at accounts counter	36
37	REC-1037	2026-02-06	2500.00	Cash payment cleared at accounts counter	37
38	REC-1038	2026-03-17	2800.00	Cash payment cleared at accounts counter	38
39	REC-1039	2026-03-08	9000.00	Cash payment cleared at accounts counter	39
40	REC-1040	2026-05-10	9000.00	Cash payment cleared at accounts counter	40
49	REC-1049	2026-06-04	39000.00	Cash payment cleared at accounts counter	49
50	REC-1050	2026-07-08	20400.00	Cash payment cleared at accounts counter	50
41	REC-1041	2026-05-09	3200.00	Cash payment cleared at accounts counter	41
60	REC-1058	2026-09-11	600.00	Family Payment: FAM-0001 (Moiz Ahmad).	1
\.


--
-- Data for Name: finance_feepaymentreceipt_month_entries; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.finance_feepaymentreceipt_month_entries (id, feepaymentreceipt_id, studentfeemonthentry_id) FROM stdin;
1	1	8
2	1	9
3	2	16
4	3	27
5	3	28
6	4	42
7	5	49
8	5	50
9	5	51
10	6	69
11	7	82
12	8	88
13	8	89
14	9	107
15	10	116
16	10	117
17	10	118
18	11	130
19	11	131
20	12	141
21	13	146
22	13	147
23	13	148
24	14	168
25	15	176
26	15	177
27	16	183
28	16	184
29	16	185
30	17	199
31	17	200
32	17	201
33	18	216
34	19	224
35	19	225
36	19	226
37	20	239
38	20	240
39	21	243
40	21	244
41	22	264
42	23	265
43	23	266
44	23	267
45	24	283
46	24	284
47	24	285
48	25	300
49	26	312
50	27	321
51	27	322
52	28	332
53	28	333
54	28	334
55	29	346
56	29	347
57	30	354
58	31	371
59	31	372
60	32	378
61	32	379
62	32	380
63	33	388
64	33	389
65	34	397
66	34	398
67	34	399
68	35	411
69	36	430
70	36	431
71	37	444
72	38	456
73	39	465
74	39	466
75	40	475
76	40	476
77	41	490
78	42	494
79	42	495
80	43	506
81	43	507
82	44	528
83	45	539
84	45	540
85	46	550
86	47	556
87	47	557
88	48	574
89	48	575
90	49	579
91	49	580
92	49	581
93	50	596
94	50	597
95	51	820
96	51	821
97	52	684
98	53	10
99	53	11
100	54	17
101	55	12
105	59	92
106	60	11
\.


--
-- Data for Name: finance_studentfeeledger; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.finance_studentfeeledger (id, created_at, academic_session_id, student_id) FROM stdin;
161	2026-09-10 18:53:34.738276-07	2	163
1	2026-09-03 22:55:29.413-07	2	1
2	2026-09-03 22:55:29.443-07	2	2
3	2026-09-03 22:55:29.469-07	2	3
4	2026-09-03 22:55:29.493-07	2	4
5	2026-09-03 22:55:29.52-07	2	5
6	2026-09-03 22:55:29.543-07	2	6
7	2026-09-03 22:55:29.565-07	2	7
8	2026-09-03 22:55:29.589-07	2	8
9	2026-09-03 22:55:29.611-07	2	9
10	2026-09-03 22:55:29.641-07	2	10
11	2026-09-03 22:55:29.665-07	2	11
12	2026-09-03 22:55:29.69-07	2	12
13	2026-09-03 22:55:29.719-07	2	13
152	2026-09-04 19:43:29.464626-07	3	3
153	2026-09-04 19:43:29.538686-07	3	21
154	2026-09-04 19:43:29.588326-07	3	39
155	2026-09-04 19:43:29.612281-07	3	57
160	2026-09-08 19:39:22.701642-07	2	152
14	2026-09-03 22:55:29.744-07	2	14
15	2026-09-03 22:55:29.77-07	2	15
16	2026-09-03 22:55:29.793-07	2	16
17	2026-09-03 22:55:29.816-07	2	17
18	2026-09-03 22:55:29.84-07	2	18
19	2026-09-03 22:55:29.864-07	2	19
20	2026-09-03 22:55:29.891-07	2	20
21	2026-09-03 22:55:29.914-07	2	21
22	2026-09-03 22:55:29.938-07	2	22
23	2026-09-03 22:55:29.96-07	2	23
24	2026-09-03 22:55:29.987-07	2	24
25	2026-09-03 22:55:30.01-07	2	25
26	2026-09-03 22:55:30.032-07	2	26
27	2026-09-03 22:55:30.057-07	2	27
28	2026-09-03 22:55:30.079-07	2	28
29	2026-09-03 22:55:30.103-07	2	29
30	2026-09-03 22:55:30.126-07	2	30
31	2026-09-03 22:55:30.148-07	2	31
32	2026-09-03 22:55:30.171-07	2	32
33	2026-09-03 22:55:30.194-07	2	33
34	2026-09-03 22:55:30.216-07	2	34
35	2026-09-03 22:55:30.24-07	2	35
36	2026-09-03 22:55:30.262-07	2	36
37	2026-09-03 22:55:30.286-07	2	37
38	2026-09-03 22:55:30.308-07	2	38
39	2026-09-03 22:55:30.331-07	2	39
40	2026-09-03 22:55:30.356-07	2	40
41	2026-09-03 22:55:30.379-07	2	41
42	2026-09-03 22:55:30.405-07	2	42
43	2026-09-03 22:55:30.427-07	2	43
44	2026-09-03 22:55:30.448-07	2	44
45	2026-09-03 22:55:30.473-07	2	45
46	2026-09-03 22:55:30.495-07	2	46
47	2026-09-03 22:55:30.52-07	2	47
48	2026-09-03 22:55:30.543-07	2	48
49	2026-09-03 22:55:30.568-07	2	49
50	2026-09-03 22:55:30.592-07	2	50
51	2026-09-03 22:55:30.615-07	2	51
52	2026-09-03 22:55:30.641-07	2	52
53	2026-09-03 22:55:30.665-07	2	53
54	2026-09-03 22:55:30.696-07	2	54
55	2026-09-03 22:55:30.721-07	2	55
56	2026-09-03 22:55:30.744-07	2	56
57	2026-09-03 22:55:30.769-07	2	57
58	2026-09-03 22:55:30.797-07	2	58
59	2026-09-03 22:55:30.823-07	2	59
60	2026-09-03 22:55:30.85-07	2	60
61	2026-09-03 22:55:30.874-07	2	61
62	2026-09-03 22:55:30.899-07	2	62
63	2026-09-03 22:55:30.924-07	2	63
64	2026-09-03 22:55:30.948-07	2	64
65	2026-09-03 22:55:30.972-07	2	65
66	2026-09-03 22:55:30.996-07	2	66
67	2026-09-03 22:55:31.02-07	2	67
68	2026-09-03 22:55:31.043-07	2	68
69	2026-09-03 22:55:31.068-07	2	69
70	2026-09-03 22:55:31.092-07	2	70
71	2026-09-03 22:55:31.116-07	2	71
72	2026-09-03 22:55:31.14-07	2	72
73	2026-09-03 22:55:31.163-07	2	73
74	2026-09-03 22:55:31.187-07	2	74
75	2026-09-03 22:55:31.21-07	2	75
\.


--
-- Data for Name: finance_studentfeemonthentry; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.finance_studentfeemonthentry (id, month, arrears, monthly_fee, exam_fee, other_charges, paid_amount, is_paid, last_payment_date, last_receipt_no, ledger_id) FROM stdin;
1921	1	0.00	0.00	0.00	0.00	0.00	t	\N		161
1922	2	0.00	0.00	0.00	0.00	0.00	t	\N		161
1923	3	0.00	0.00	0.00	0.00	0.00	t	\N		161
1924	4	0.00	0.00	0.00	0.00	0.00	t	\N		161
1925	5	0.00	0.00	0.00	0.00	0.00	t	\N		161
1926	6	0.00	0.00	0.00	0.00	0.00	t	\N		161
1927	7	0.00	0.00	0.00	0.00	0.00	t	\N		161
1928	8	0.00	0.00	0.00	0.00	0.00	t	\N		161
1929	9	0.00	4800.00	0.00	0.00	0.00	f	\N		161
1930	10	4800.00	4800.00	0.00	0.00	0.00	f	\N		161
1931	11	9600.00	4800.00	0.00	0.00	0.00	f	\N		161
1932	12	14400.00	4800.00	0.00	0.00	0.00	f	\N		161
1	1	0.00	0.00	0.00	0.00	0.00	t	\N		1
2	2	0.00	0.00	0.00	0.00	0.00	t	\N		1
673	1	0.00	0.00	0.00	0.00	0.00	t	\N		57
674	2	0.00	0.00	0.00	0.00	0.00	t	\N		57
675	3	0.00	0.00	0.00	0.00	0.00	t	\N		57
676	4	0.00	0.00	0.00	0.00	0.00	t	\N		57
677	5	0.00	0.00	0.00	0.00	0.00	t	\N		57
678	6	0.00	0.00	0.00	0.00	0.00	t	\N		57
679	7	0.00	0.00	0.00	0.00	0.00	t	\N		57
680	8	0.00	0.00	0.00	0.00	0.00	t	\N		57
681	9	0.00	0.00	0.00	0.00	0.00	t	\N		57
682	10	0.00	0.00	0.00	0.00	0.00	t	\N		57
683	11	0.00	0.00	0.00	0.00	0.00	t	\N		57
684	12	0.00	3000.00	0.00	0.00	0.00	f	\N		57
22	10	14000.00	2800.00	0.00	0.00	0.00	f	\N		2
23	11	16800.00	2800.00	0.00	0.00	0.00	f	\N		2
24	12	19600.00	2800.00	0.00	0.00	0.00	f	\N		2
25	1	0.00	0.00	0.00	0.00	0.00	t	\N		3
26	2	0.00	0.00	0.00	0.00	0.00	t	\N		3
51	3	0.00	3200.00	0.00	0.00	9600.00	t	2026-03-21	REC-1005	5
52	4	0.00	3200.00	0.00	0.00	0.00	f	\N		5
53	5	3200.00	3200.00	0.00	0.00	0.00	f	\N		5
54	6	6400.00	3200.00	0.00	0.00	0.00	f	\N		5
55	7	9600.00	3200.00	0.00	0.00	0.00	f	\N		5
56	8	12800.00	3200.00	0.00	0.00	0.00	f	\N		5
57	9	16000.00	3200.00	0.00	0.00	0.00	f	\N		5
58	10	19200.00	3200.00	0.00	0.00	0.00	f	\N		5
59	11	22400.00	3200.00	0.00	0.00	0.00	f	\N		5
60	12	25600.00	3200.00	0.00	0.00	0.00	f	\N		5
61	1	0.00	0.00	0.00	0.00	0.00	t	\N		6
62	2	0.00	0.00	0.00	0.00	0.00	t	\N		6
63	3	0.00	0.00	0.00	0.00	0.00	t	\N		6
64	4	0.00	0.00	0.00	0.00	0.00	t	\N		6
65	5	0.00	0.00	0.00	0.00	0.00	t	\N		6
66	6	0.00	0.00	0.00	0.00	0.00	t	\N		6
67	7	0.00	0.00	0.00	0.00	0.00	t	\N		6
68	8	0.00	0.00	0.00	0.00	0.00	t	\N		6
113	5	0.00	0.00	0.00	0.00	0.00	t	\N		10
114	6	0.00	0.00	0.00	0.00	0.00	t	\N		10
115	7	0.00	0.00	0.00	0.00	0.00	t	\N		10
27	3	0.00	3000.00	0.00	0.00	3000.00	t	2026-04-23	REC-1003	3
28	4	0.00	3000.00	0.00	0.00	6000.00	t	2026-04-23	REC-1003	3
29	5	0.00	3000.00	0.00	0.00	0.00	f	\N		3
30	6	3000.00	3000.00	0.00	0.00	0.00	f	\N		3
31	7	6000.00	3000.00	0.00	0.00	0.00	f	\N		3
32	8	9000.00	3000.00	0.00	0.00	0.00	f	\N		3
33	9	12000.00	3000.00	0.00	0.00	0.00	f	\N		3
34	10	15000.00	3000.00	0.00	0.00	0.00	f	\N		3
35	11	18000.00	3000.00	0.00	0.00	0.00	f	\N		3
36	12	21000.00	3000.00	0.00	0.00	0.00	f	\N		3
37	1	0.00	0.00	0.00	0.00	0.00	t	\N		4
38	2	0.00	0.00	0.00	0.00	0.00	t	\N		4
39	3	0.00	0.00	0.00	0.00	0.00	t	\N		4
40	4	0.00	0.00	0.00	0.00	0.00	t	\N		4
41	5	0.00	0.00	0.00	0.00	0.00	t	\N		4
42	6	0.00	3000.00	0.00	0.00	3000.00	t	2026-03-09	REC-1004	4
43	7	0.00	3000.00	0.00	0.00	0.00	f	\N		4
44	8	3000.00	3000.00	0.00	0.00	0.00	f	\N		4
45	9	6000.00	3000.00	0.00	0.00	0.00	f	\N		4
46	10	9000.00	3000.00	0.00	0.00	0.00	f	\N		4
47	11	12000.00	3000.00	0.00	0.00	0.00	f	\N		4
48	12	15000.00	3000.00	0.00	0.00	0.00	f	\N		4
49	1	0.00	3200.00	0.00	0.00	3200.00	t	2026-03-21	REC-1005	5
50	2	0.00	3200.00	0.00	0.00	6400.00	t	2026-03-21	REC-1005	5
69	9	0.00	3200.00	0.00	0.00	3200.00	t	2026-08-28	REC-1006	6
70	10	0.00	3200.00	0.00	0.00	0.00	f	\N		6
71	11	3200.00	3200.00	0.00	0.00	0.00	f	\N		6
72	12	6400.00	3200.00	0.00	0.00	0.00	f	\N		6
73	1	0.00	0.00	0.00	0.00	0.00	t	\N		7
74	2	0.00	0.00	0.00	0.00	0.00	t	\N		7
116	8	0.00	4200.00	0.00	0.00	4200.00	t	2026-07-18	REC-1010	10
117	9	0.00	4200.00	0.00	0.00	8400.00	t	2026-07-18	REC-1010	10
118	10	0.00	4200.00	0.00	0.00	12600.00	t	2026-07-18	REC-1010	10
119	11	0.00	4200.00	0.00	0.00	0.00	f	\N		10
120	12	4200.00	4200.00	0.00	0.00	0.00	f	\N		10
121	1	0.00	0.00	0.00	0.00	0.00	t	\N		11
122	2	0.00	0.00	0.00	0.00	0.00	t	\N		11
123	3	0.00	0.00	0.00	0.00	0.00	t	\N		11
124	4	0.00	0.00	0.00	0.00	0.00	t	\N		11
125	5	0.00	0.00	0.00	0.00	0.00	t	\N		11
126	6	0.00	0.00	0.00	0.00	0.00	t	\N		11
127	7	0.00	0.00	0.00	0.00	0.00	t	\N		11
128	8	0.00	0.00	0.00	0.00	0.00	t	\N		11
129	9	0.00	0.00	0.00	0.00	0.00	t	\N		11
130	10	0.00	4800.00	0.00	0.00	4800.00	t	2026-03-10	REC-1011	11
131	11	0.00	4800.00	0.00	0.00	9600.00	t	2026-03-10	REC-1011	11
132	12	0.00	4800.00	0.00	0.00	0.00	f	\N		11
133	1	0.00	0.00	0.00	0.00	0.00	t	\N		12
134	2	0.00	0.00	0.00	0.00	0.00	t	\N		12
135	3	0.00	0.00	0.00	0.00	0.00	t	\N		12
136	4	0.00	0.00	0.00	0.00	0.00	t	\N		12
137	5	0.00	0.00	0.00	0.00	0.00	t	\N		12
138	6	0.00	0.00	0.00	0.00	0.00	t	\N		12
139	7	0.00	0.00	0.00	0.00	0.00	t	\N		12
140	8	0.00	0.00	0.00	0.00	0.00	t	\N		12
141	9	0.00	5000.00	0.00	0.00	5000.00	t	2026-07-20	REC-1012	12
142	10	0.00	5000.00	0.00	0.00	0.00	f	\N		12
143	11	5000.00	5000.00	0.00	0.00	0.00	f	\N		12
144	12	10000.00	5000.00	0.00	0.00	0.00	f	\N		12
145	1	0.00	0.00	0.00	0.00	0.00	t	\N		13
146	2	0.00	6500.00	0.00	0.00	6500.00	t	2026-02-11	REC-1013	13
147	3	0.00	6500.00	0.00	0.00	13000.00	t	2026-02-11	REC-1013	13
148	4	0.00	6500.00	0.00	0.00	19500.00	t	2026-02-11	REC-1013	13
149	5	0.00	6500.00	0.00	0.00	0.00	f	\N		13
150	6	6500.00	6500.00	0.00	0.00	0.00	f	\N		13
151	7	13000.00	6500.00	0.00	0.00	0.00	f	\N		13
152	8	19500.00	6500.00	0.00	0.00	0.00	f	\N		13
153	9	26000.00	6500.00	0.00	0.00	0.00	f	\N		13
75	3	0.00	0.00	0.00	0.00	0.00	t	\N		7
76	4	0.00	0.00	0.00	0.00	0.00	t	\N		7
77	5	0.00	0.00	0.00	0.00	0.00	t	\N		7
78	6	0.00	0.00	0.00	0.00	0.00	t	\N		7
1813	1	0.00	3200.00	0.00	0.00	0.00	f	\N		152
1814	2	3200.00	3200.00	0.00	0.00	0.00	f	\N		152
79	7	0.00	0.00	0.00	0.00	0.00	t	\N		7
80	8	0.00	0.00	0.00	0.00	0.00	t	\N		7
81	9	0.00	0.00	0.00	0.00	0.00	t	\N		7
82	10	0.00	3500.00	0.00	0.00	3500.00	t	2026-03-02	REC-1007	7
83	11	0.00	3500.00	0.00	0.00	0.00	f	\N		7
154	10	32500.00	6500.00	0.00	0.00	0.00	f	\N		13
155	11	39000.00	6500.00	0.00	0.00	0.00	f	\N		13
156	12	45500.00	6500.00	0.00	0.00	0.00	f	\N		13
157	1	0.00	0.00	0.00	0.00	0.00	t	\N		14
158	2	0.00	0.00	0.00	0.00	0.00	t	\N		14
159	3	0.00	0.00	0.00	0.00	0.00	t	\N		14
160	4	0.00	0.00	0.00	0.00	0.00	t	\N		14
161	5	0.00	0.00	0.00	0.00	0.00	t	\N		14
162	6	0.00	0.00	0.00	0.00	0.00	t	\N		14
163	7	0.00	0.00	0.00	0.00	0.00	t	\N		14
164	8	0.00	0.00	0.00	0.00	0.00	t	\N		14
165	9	0.00	0.00	0.00	0.00	0.00	t	\N		14
166	10	0.00	0.00	0.00	0.00	0.00	t	\N		14
167	11	0.00	0.00	0.00	0.00	0.00	t	\N		14
168	12	0.00	6800.00	0.00	0.00	6800.00	t	2026-01-22	REC-1014	14
169	1	0.00	0.00	0.00	0.00	0.00	t	\N		15
170	2	0.00	0.00	0.00	0.00	0.00	t	\N		15
171	3	0.00	0.00	0.00	0.00	0.00	t	\N		15
172	4	0.00	0.00	0.00	0.00	0.00	t	\N		15
173	5	0.00	0.00	0.00	0.00	0.00	t	\N		15
174	6	0.00	0.00	0.00	0.00	0.00	t	\N		15
175	7	0.00	0.00	0.00	0.00	0.00	t	\N		15
176	8	0.00	6500.00	0.00	0.00	6500.00	t	2026-02-21	REC-1015	15
177	9	0.00	6500.00	0.00	0.00	13000.00	t	2026-02-21	REC-1015	15
178	10	0.00	6500.00	0.00	0.00	0.00	f	\N		15
179	11	6500.00	6500.00	0.00	0.00	0.00	f	\N		15
180	12	13000.00	6500.00	0.00	0.00	0.00	f	\N		15
181	1	0.00	0.00	0.00	0.00	0.00	t	\N		16
182	2	0.00	0.00	0.00	0.00	0.00	t	\N		16
183	3	0.00	6800.00	0.00	0.00	6800.00	t	2026-01-03	REC-1016	16
184	4	0.00	6800.00	0.00	0.00	13600.00	t	2026-01-03	REC-1016	16
185	5	0.00	6800.00	0.00	0.00	20400.00	t	2026-01-03	REC-1016	16
186	6	0.00	6800.00	0.00	0.00	0.00	f	\N		16
187	7	6800.00	6800.00	0.00	0.00	0.00	f	\N		16
1815	3	6400.00	3200.00	0.00	0.00	0.00	f	\N		152
84	12	3500.00	3500.00	0.00	0.00	0.00	f	\N		7
1816	4	9600.00	3200.00	0.00	0.00	0.00	f	\N		152
1817	5	12800.00	3200.00	0.00	0.00	0.00	f	\N		152
1818	6	16000.00	3200.00	0.00	0.00	0.00	f	\N		152
188	8	13600.00	6800.00	0.00	0.00	0.00	f	\N		16
189	9	20400.00	6800.00	0.00	0.00	0.00	f	\N		16
190	10	27200.00	6800.00	0.00	0.00	0.00	f	\N		16
191	11	34000.00	6800.00	0.00	0.00	0.00	f	\N		16
192	12	40800.00	6800.00	0.00	0.00	0.00	f	\N		16
193	1	0.00	0.00	0.00	0.00	0.00	t	\N		17
194	2	0.00	0.00	0.00	0.00	0.00	t	\N		17
195	3	0.00	0.00	0.00	0.00	0.00	t	\N		17
196	4	0.00	0.00	0.00	0.00	0.00	t	\N		17
197	5	0.00	0.00	0.00	0.00	0.00	t	\N		17
198	6	0.00	0.00	0.00	0.00	0.00	t	\N		17
199	7	0.00	6000.00	0.00	0.00	6000.00	t	2026-07-16	REC-1017	17
200	8	0.00	6000.00	0.00	0.00	12000.00	t	2026-07-16	REC-1017	17
201	9	0.00	6000.00	0.00	0.00	18000.00	t	2026-07-16	REC-1017	17
202	10	0.00	6000.00	0.00	0.00	0.00	f	\N		17
203	11	6000.00	6000.00	0.00	0.00	0.00	f	\N		17
204	12	12000.00	6000.00	0.00	0.00	0.00	f	\N		17
205	1	0.00	0.00	0.00	0.00	0.00	t	\N		18
206	2	0.00	0.00	0.00	0.00	0.00	t	\N		18
207	3	0.00	0.00	0.00	0.00	0.00	t	\N		18
208	4	0.00	0.00	0.00	0.00	0.00	t	\N		18
209	5	0.00	0.00	0.00	0.00	0.00	t	\N		18
210	6	0.00	0.00	0.00	0.00	0.00	t	\N		18
211	7	0.00	0.00	0.00	0.00	0.00	t	\N		18
212	8	0.00	0.00	0.00	0.00	0.00	t	\N		18
213	9	0.00	0.00	0.00	0.00	0.00	t	\N		18
214	10	0.00	0.00	0.00	0.00	0.00	t	\N		18
215	11	0.00	0.00	0.00	0.00	0.00	t	\N		18
216	12	0.00	6200.00	0.00	0.00	6200.00	t	2026-07-15	REC-1018	18
217	1	0.00	0.00	0.00	0.00	0.00	t	\N		19
218	2	0.00	0.00	0.00	0.00	0.00	t	\N		19
219	3	0.00	0.00	0.00	0.00	0.00	t	\N		19
220	4	0.00	0.00	0.00	0.00	0.00	t	\N		19
221	5	0.00	0.00	0.00	0.00	0.00	t	\N		19
222	6	0.00	0.00	0.00	0.00	0.00	t	\N		19
223	7	0.00	0.00	0.00	0.00	0.00	t	\N		19
224	8	0.00	2500.00	0.00	0.00	2500.00	t	2026-06-09	REC-1019	19
225	9	0.00	2500.00	0.00	0.00	5000.00	t	2026-06-09	REC-1019	19
1819	7	19200.00	3200.00	0.00	0.00	0.00	f	\N		152
1820	8	22400.00	3200.00	0.00	0.00	0.00	f	\N		152
90	6	0.00	3800.00	0.00	0.00	0.00	f	\N		8
1821	9	25600.00	3200.00	0.00	0.00	0.00	f	\N		152
1822	10	28800.00	3200.00	0.00	0.00	0.00	f	\N		152
1823	11	32000.00	3200.00	0.00	0.00	0.00	f	\N		152
1824	12	35200.00	3200.00	0.00	0.00	0.00	f	\N		152
226	10	0.00	2500.00	0.00	0.00	7500.00	t	2026-06-09	REC-1019	19
227	11	0.00	2500.00	0.00	0.00	0.00	f	\N		19
228	12	2500.00	2500.00	0.00	0.00	0.00	f	\N		19
229	1	0.00	0.00	0.00	0.00	0.00	t	\N		20
230	2	0.00	0.00	0.00	0.00	0.00	t	\N		20
231	3	0.00	0.00	0.00	0.00	0.00	t	\N		20
232	4	0.00	0.00	0.00	0.00	0.00	t	\N		20
233	5	0.00	0.00	0.00	0.00	0.00	t	\N		20
234	6	0.00	0.00	0.00	0.00	0.00	t	\N		20
235	7	0.00	0.00	0.00	0.00	0.00	t	\N		20
236	8	0.00	0.00	0.00	0.00	0.00	t	\N		20
237	9	0.00	0.00	0.00	0.00	0.00	t	\N		20
238	10	0.00	0.00	0.00	0.00	0.00	t	\N		20
239	11	0.00	2800.00	0.00	0.00	2800.00	t	2026-08-14	REC-1020	20
240	12	0.00	2800.00	0.00	0.00	5600.00	t	2026-08-14	REC-1020	20
241	1	0.00	0.00	0.00	0.00	0.00	t	\N		21
242	2	0.00	0.00	0.00	0.00	0.00	t	\N		21
243	3	0.00	3000.00	0.00	0.00	3000.00	t	2026-08-16	REC-1021	21
244	4	0.00	3000.00	0.00	0.00	6000.00	t	2026-08-16	REC-1021	21
245	5	0.00	3000.00	0.00	0.00	0.00	f	\N		21
246	6	3000.00	3000.00	0.00	0.00	0.00	f	\N		21
247	7	6000.00	3000.00	0.00	0.00	0.00	f	\N		21
248	8	9000.00	3000.00	0.00	0.00	0.00	f	\N		21
249	9	12000.00	3000.00	0.00	0.00	0.00	f	\N		21
250	10	15000.00	3000.00	0.00	0.00	0.00	f	\N		21
251	11	18000.00	3000.00	0.00	0.00	0.00	f	\N		21
252	12	21000.00	3000.00	0.00	0.00	0.00	f	\N		21
253	1	0.00	0.00	0.00	0.00	0.00	t	\N		22
254	2	0.00	0.00	0.00	0.00	0.00	t	\N		22
255	3	0.00	0.00	0.00	0.00	0.00	t	\N		22
256	4	0.00	0.00	0.00	0.00	0.00	t	\N		22
257	5	0.00	0.00	0.00	0.00	0.00	t	\N		22
258	6	0.00	0.00	0.00	0.00	0.00	t	\N		22
259	7	0.00	0.00	0.00	0.00	0.00	t	\N		22
260	8	0.00	0.00	0.00	0.00	0.00	t	\N		22
261	9	0.00	0.00	0.00	0.00	0.00	t	\N		22
262	10	0.00	0.00	0.00	0.00	0.00	t	\N		22
1825	1	0.00	3200.00	0.00	0.00	0.00	f	\N		153
1826	2	3200.00	3200.00	0.00	0.00	0.00	f	\N		153
1827	3	6400.00	3200.00	0.00	0.00	0.00	f	\N		153
96	12	16400.00	2500.00	0.00	0.00	0.00	f	\N		8
97	1	0.00	0.00	0.00	0.00	0.00	t	\N		9
263	11	0.00	0.00	0.00	0.00	0.00	t	\N		22
264	12	0.00	3000.00	0.00	0.00	3000.00	t	2026-04-22	REC-1022	22
265	1	0.00	3200.00	0.00	0.00	3200.00	t	2026-05-11	REC-1023	23
266	2	0.00	3200.00	0.00	0.00	6400.00	t	2026-05-11	REC-1023	23
267	3	0.00	3200.00	0.00	0.00	9600.00	t	2026-05-11	REC-1023	23
268	4	0.00	3200.00	0.00	0.00	0.00	f	\N		23
269	5	3200.00	3200.00	0.00	0.00	0.00	f	\N		23
270	6	6400.00	3200.00	0.00	0.00	0.00	f	\N		23
271	7	9600.00	3200.00	0.00	0.00	0.00	f	\N		23
272	8	12800.00	3200.00	0.00	0.00	0.00	f	\N		23
273	9	16000.00	3200.00	0.00	0.00	0.00	f	\N		23
274	10	19200.00	3200.00	0.00	0.00	0.00	f	\N		23
275	11	22400.00	3200.00	0.00	0.00	0.00	f	\N		23
276	12	25600.00	3200.00	0.00	0.00	0.00	f	\N		23
277	1	0.00	0.00	0.00	0.00	0.00	t	\N		24
278	2	0.00	0.00	0.00	0.00	0.00	t	\N		24
279	3	0.00	0.00	0.00	0.00	0.00	t	\N		24
280	4	0.00	0.00	0.00	0.00	0.00	t	\N		24
281	5	0.00	0.00	0.00	0.00	0.00	t	\N		24
282	6	0.00	0.00	0.00	0.00	0.00	t	\N		24
283	7	0.00	3200.00	0.00	0.00	3200.00	t	2026-06-22	REC-1024	24
284	8	0.00	3200.00	0.00	0.00	6400.00	t	2026-06-22	REC-1024	24
285	9	0.00	3200.00	0.00	0.00	9600.00	t	2026-06-22	REC-1024	24
286	10	0.00	3200.00	0.00	0.00	0.00	f	\N		24
287	11	3200.00	3200.00	0.00	0.00	0.00	f	\N		24
288	12	6400.00	3200.00	0.00	0.00	0.00	f	\N		24
289	1	0.00	0.00	0.00	0.00	0.00	t	\N		25
290	2	0.00	0.00	0.00	0.00	0.00	t	\N		25
291	3	0.00	0.00	0.00	0.00	0.00	t	\N		25
292	4	0.00	0.00	0.00	0.00	0.00	t	\N		25
293	5	0.00	0.00	0.00	0.00	0.00	t	\N		25
294	6	0.00	0.00	0.00	0.00	0.00	t	\N		25
295	7	0.00	0.00	0.00	0.00	0.00	t	\N		25
296	8	0.00	0.00	0.00	0.00	0.00	t	\N		25
297	9	0.00	0.00	0.00	0.00	0.00	t	\N		25
298	10	0.00	0.00	0.00	0.00	0.00	t	\N		25
299	11	0.00	0.00	0.00	0.00	0.00	t	\N		25
300	12	0.00	3500.00	0.00	0.00	3500.00	t	2026-06-21	REC-1025	25
301	1	0.00	0.00	0.00	0.00	0.00	t	\N		26
302	2	0.00	0.00	0.00	0.00	0.00	t	\N		26
303	3	0.00	0.00	0.00	0.00	0.00	t	\N		26
304	4	0.00	0.00	0.00	0.00	0.00	t	\N		26
305	5	0.00	0.00	0.00	0.00	0.00	t	\N		26
306	6	0.00	0.00	0.00	0.00	0.00	t	\N		26
307	7	0.00	0.00	0.00	0.00	0.00	t	\N		26
308	8	0.00	0.00	0.00	0.00	0.00	t	\N		26
1828	4	9600.00	3200.00	0.00	0.00	0.00	f	\N		153
1829	5	12800.00	3200.00	0.00	0.00	0.00	f	\N		153
98	2	0.00	0.00	0.00	0.00	0.00	t	\N		9
99	3	0.00	0.00	0.00	0.00	0.00	t	\N		9
100	4	0.00	0.00	0.00	0.00	0.00	t	\N		9
101	5	0.00	0.00	0.00	0.00	0.00	t	\N		9
102	6	0.00	0.00	0.00	0.00	0.00	t	\N		9
103	7	0.00	0.00	0.00	0.00	0.00	t	\N		9
104	8	0.00	0.00	0.00	0.00	0.00	t	\N		9
105	9	0.00	0.00	0.00	0.00	0.00	t	\N		9
1830	6	16000.00	3200.00	0.00	0.00	0.00	f	\N		153
1831	7	19200.00	3200.00	0.00	0.00	0.00	f	\N		153
1832	8	22400.00	3200.00	0.00	0.00	0.00	f	\N		153
1833	9	25600.00	3200.00	0.00	0.00	0.00	f	\N		153
1834	10	28800.00	3200.00	0.00	0.00	0.00	f	\N		153
309	9	0.00	0.00	0.00	0.00	0.00	t	\N		26
310	10	0.00	0.00	0.00	0.00	0.00	t	\N		26
311	11	0.00	0.00	0.00	0.00	0.00	t	\N		26
312	12	0.00	3800.00	0.00	0.00	3800.00	t	2026-04-27	REC-1026	26
313	1	0.00	0.00	0.00	0.00	0.00	t	\N		27
314	2	0.00	0.00	0.00	0.00	0.00	t	\N		27
315	3	0.00	0.00	0.00	0.00	0.00	t	\N		27
316	4	0.00	0.00	0.00	0.00	0.00	t	\N		27
317	5	0.00	0.00	0.00	0.00	0.00	t	\N		27
318	6	0.00	0.00	0.00	0.00	0.00	t	\N		27
319	7	0.00	0.00	0.00	0.00	0.00	t	\N		27
320	8	0.00	0.00	0.00	0.00	0.00	t	\N		27
321	9	0.00	4000.00	0.00	0.00	4000.00	t	2026-08-10	REC-1027	27
322	10	0.00	4000.00	0.00	0.00	8000.00	t	2026-08-10	REC-1027	27
323	11	0.00	4000.00	0.00	0.00	0.00	f	\N		27
324	12	4000.00	4000.00	0.00	0.00	0.00	f	\N		27
325	1	0.00	0.00	0.00	0.00	0.00	t	\N		28
326	2	0.00	0.00	0.00	0.00	0.00	t	\N		28
327	3	0.00	0.00	0.00	0.00	0.00	t	\N		28
328	4	0.00	0.00	0.00	0.00	0.00	t	\N		28
329	5	0.00	0.00	0.00	0.00	0.00	t	\N		28
330	6	0.00	0.00	0.00	0.00	0.00	t	\N		28
331	7	0.00	0.00	0.00	0.00	0.00	t	\N		28
332	8	0.00	4200.00	0.00	0.00	4200.00	t	2026-01-11	REC-1028	28
333	9	0.00	4200.00	0.00	0.00	8400.00	t	2026-01-11	REC-1028	28
334	10	0.00	4200.00	0.00	0.00	12600.00	t	2026-01-11	REC-1028	28
335	11	0.00	4200.00	0.00	0.00	0.00	f	\N		28
336	12	4200.00	4200.00	0.00	0.00	0.00	f	\N		28
337	1	0.00	0.00	0.00	0.00	0.00	t	\N		29
338	2	0.00	0.00	0.00	0.00	0.00	t	\N		29
339	3	0.00	0.00	0.00	0.00	0.00	t	\N		29
340	4	0.00	0.00	0.00	0.00	0.00	t	\N		29
341	5	0.00	0.00	0.00	0.00	0.00	t	\N		29
342	6	0.00	0.00	0.00	0.00	0.00	t	\N		29
343	7	0.00	0.00	0.00	0.00	0.00	t	\N		29
344	8	0.00	0.00	0.00	0.00	0.00	t	\N		29
1835	11	32000.00	3200.00	0.00	0.00	0.00	f	\N		153
1836	12	35200.00	3200.00	0.00	0.00	0.00	f	\N		153
106	10	0.00	0.00	0.00	0.00	0.00	t	\N		9
107	11	0.00	4000.00	0.00	0.00	4000.00	t	2026-01-26	REC-1009	9
108	12	0.00	4000.00	0.00	0.00	0.00	f	\N		9
109	1	0.00	0.00	0.00	0.00	0.00	t	\N		10
110	2	0.00	0.00	0.00	0.00	0.00	t	\N		10
111	3	0.00	0.00	0.00	0.00	0.00	t	\N		10
345	9	0.00	0.00	0.00	0.00	0.00	t	\N		29
346	10	0.00	4800.00	0.00	0.00	4800.00	t	2026-06-22	REC-1029	29
347	11	0.00	4800.00	0.00	0.00	9600.00	t	2026-06-22	REC-1029	29
348	12	0.00	4800.00	0.00	0.00	0.00	f	\N		29
349	1	0.00	0.00	0.00	0.00	0.00	t	\N		30
350	2	0.00	0.00	0.00	0.00	0.00	t	\N		30
351	3	0.00	0.00	0.00	0.00	0.00	t	\N		30
352	4	0.00	0.00	0.00	0.00	0.00	t	\N		30
353	5	0.00	0.00	0.00	0.00	0.00	t	\N		30
354	6	0.00	5000.00	0.00	0.00	5000.00	t	2026-02-20	REC-1030	30
355	7	0.00	5000.00	0.00	0.00	0.00	f	\N		30
356	8	5000.00	5000.00	0.00	0.00	0.00	f	\N		30
357	9	10000.00	5000.00	0.00	0.00	0.00	f	\N		30
358	10	15000.00	5000.00	0.00	0.00	0.00	f	\N		30
359	11	20000.00	5000.00	0.00	0.00	0.00	f	\N		30
360	12	25000.00	5000.00	0.00	0.00	0.00	f	\N		30
361	1	0.00	0.00	0.00	0.00	0.00	t	\N		31
362	2	0.00	0.00	0.00	0.00	0.00	t	\N		31
363	3	0.00	0.00	0.00	0.00	0.00	t	\N		31
364	4	0.00	0.00	0.00	0.00	0.00	t	\N		31
365	5	0.00	0.00	0.00	0.00	0.00	t	\N		31
366	6	0.00	0.00	0.00	0.00	0.00	t	\N		31
367	7	0.00	0.00	0.00	0.00	0.00	t	\N		31
368	8	0.00	0.00	0.00	0.00	0.00	t	\N		31
369	9	0.00	0.00	0.00	0.00	0.00	t	\N		31
370	10	0.00	0.00	0.00	0.00	0.00	t	\N		31
371	11	0.00	6500.00	0.00	0.00	6500.00	t	2026-08-24	REC-1031	31
372	12	0.00	6500.00	0.00	0.00	13000.00	t	2026-08-24	REC-1031	31
373	1	0.00	0.00	0.00	0.00	0.00	t	\N		32
374	2	0.00	0.00	0.00	0.00	0.00	t	\N		32
375	3	0.00	0.00	0.00	0.00	0.00	t	\N		32
376	4	0.00	0.00	0.00	0.00	0.00	t	\N		32
377	5	0.00	0.00	0.00	0.00	0.00	t	\N		32
378	6	0.00	6800.00	0.00	0.00	6800.00	t	2026-07-17	REC-1032	32
379	7	0.00	6800.00	0.00	0.00	13600.00	t	2026-07-17	REC-1032	32
380	8	0.00	6800.00	0.00	0.00	20400.00	t	2026-07-17	REC-1032	32
381	9	0.00	6800.00	0.00	0.00	0.00	f	\N		32
382	10	6800.00	6800.00	0.00	0.00	0.00	f	\N		32
3	3	0.00	0.00	0.00	0.00	0.00	t	\N		1
4	4	0.00	0.00	0.00	0.00	0.00	t	\N		1
5	5	0.00	0.00	0.00	0.00	0.00	t	\N		1
6	6	0.00	0.00	0.00	0.00	0.00	t	\N		1
7	7	0.00	0.00	0.00	0.00	0.00	t	\N		1
8	8	0.00	2500.00	0.00	0.00	2500.00	t	2026-05-22	REC-1001	1
9	9	0.00	2500.00	0.00	0.00	5000.00	t	2026-05-22	REC-1001	1
10	10	0.00	2500.00	0.00	0.00	0.00	f	\N		1
11	11	2500.00	2500.00	0.00	0.00	600.00	f	2026-09-11	REC-1058	1
12	12	4400.00	2500.00	0.00	0.00	0.00	f	\N		1
1837	1	0.00	3200.00	0.00	0.00	0.00	f	\N		154
1838	2	3200.00	3200.00	0.00	0.00	0.00	f	\N		154
1839	3	6400.00	3200.00	0.00	0.00	0.00	f	\N		154
1840	4	9600.00	3200.00	0.00	0.00	0.00	f	\N		154
1841	5	12800.00	3200.00	0.00	0.00	0.00	f	\N		154
1842	6	16000.00	3200.00	0.00	0.00	0.00	f	\N		154
1843	7	19200.00	3200.00	0.00	0.00	0.00	f	\N		154
1844	8	22400.00	3200.00	0.00	0.00	0.00	f	\N		154
1845	9	25600.00	3200.00	0.00	0.00	0.00	f	\N		154
1846	10	28800.00	3200.00	0.00	0.00	0.00	f	\N		154
1847	11	32000.00	3200.00	0.00	0.00	0.00	f	\N		154
1848	12	35200.00	3200.00	0.00	0.00	0.00	f	\N		154
13	1	0.00	0.00	0.00	0.00	0.00	t	\N		2
1849	1	0.00	3200.00	0.00	0.00	0.00	f	\N		155
1850	2	3200.00	3200.00	0.00	0.00	0.00	f	\N		155
1851	3	6400.00	3200.00	0.00	0.00	0.00	f	\N		155
1852	4	9600.00	3200.00	0.00	0.00	0.00	f	\N		155
1853	5	12800.00	3200.00	0.00	0.00	0.00	f	\N		155
1854	6	16000.00	3200.00	0.00	0.00	0.00	f	\N		155
1855	7	19200.00	3200.00	0.00	0.00	0.00	f	\N		155
1856	8	22400.00	3200.00	0.00	0.00	0.00	f	\N		155
1857	9	25600.00	3200.00	0.00	0.00	0.00	f	\N		155
1858	10	28800.00	3200.00	0.00	0.00	0.00	f	\N		155
1859	11	32000.00	3200.00	0.00	0.00	0.00	f	\N		155
1860	12	35200.00	3200.00	0.00	0.00	0.00	f	\N		155
14	2	0.00	0.00	0.00	0.00	0.00	t	\N		2
15	3	0.00	0.00	0.00	0.00	0.00	t	\N		2
16	4	0.00	2800.00	0.00	0.00	2800.00	t	2026-08-17	REC-1002	2
17	5	0.00	2800.00	0.00	0.00	0.00	f	\N		2
18	6	2800.00	2800.00	0.00	0.00	0.00	f	\N		2
19	7	5600.00	2800.00	0.00	0.00	0.00	f	\N		2
20	8	8400.00	2800.00	0.00	0.00	0.00	f	\N		2
21	9	11200.00	2800.00	0.00	0.00	0.00	f	\N		2
112	4	0.00	0.00	0.00	0.00	0.00	t	\N		10
1909	1	0.00	0.00	0.00	0.00	0.00	t	\N		160
1910	2	0.00	0.00	0.00	0.00	0.00	t	\N		160
1911	3	0.00	0.00	0.00	0.00	0.00	t	\N		160
1912	4	0.00	0.00	0.00	0.00	0.00	t	\N		160
1913	5	0.00	0.00	0.00	0.00	0.00	t	\N		160
1914	6	0.00	0.00	0.00	0.00	0.00	t	\N		160
1915	7	0.00	0.00	0.00	0.00	0.00	t	\N		160
1916	8	0.00	0.00	0.00	0.00	0.00	t	\N		160
1917	9	0.00	2500.00	0.00	0.00	0.00	f	\N		160
1918	10	2500.00	2500.00	0.00	0.00	0.00	f	\N		160
1919	11	5000.00	2500.00	0.00	0.00	0.00	f	\N		160
1920	12	7500.00	2500.00	0.00	0.00	0.00	f	\N		160
85	1	0.00	0.00	0.00	0.00	0.00	t	\N		8
86	2	0.00	0.00	0.00	0.00	0.00	t	\N		8
87	3	0.00	0.00	0.00	0.00	0.00	t	\N		8
88	4	0.00	3800.00	0.00	0.00	3800.00	t	2026-05-03	REC-1008	8
89	5	0.00	3800.00	0.00	0.00	7600.00	t	2026-05-03	REC-1008	8
91	7	3800.00	3800.00	0.00	0.00	0.00	f	\N		8
92	8	7600.00	2500.00	0.00	0.00	1200.00	f	2026-09-09	REC-1057	8
93	9	8900.00	2500.00	0.00	0.00	0.00	f	\N		8
94	10	11400.00	2500.00	0.00	0.00	0.00	f	\N		8
95	11	13900.00	2500.00	0.00	0.00	0.00	f	\N		8
383	11	13600.00	6800.00	0.00	0.00	0.00	f	\N		32
384	12	20400.00	6800.00	0.00	0.00	0.00	f	\N		32
385	1	0.00	0.00	0.00	0.00	0.00	t	\N		33
386	2	0.00	0.00	0.00	0.00	0.00	t	\N		33
387	3	0.00	0.00	0.00	0.00	0.00	t	\N		33
388	4	0.00	6500.00	0.00	0.00	6500.00	t	2026-08-28	REC-1033	33
389	5	0.00	6500.00	0.00	0.00	13000.00	t	2026-08-28	REC-1033	33
390	6	0.00	6500.00	0.00	0.00	0.00	f	\N		33
391	7	6500.00	6500.00	0.00	0.00	0.00	f	\N		33
392	8	13000.00	6500.00	0.00	0.00	0.00	f	\N		33
393	9	19500.00	6500.00	0.00	0.00	0.00	f	\N		33
394	10	26000.00	6500.00	0.00	0.00	0.00	f	\N		33
395	11	32500.00	6500.00	0.00	0.00	0.00	f	\N		33
396	12	39000.00	6500.00	0.00	0.00	0.00	f	\N		33
397	1	0.00	6800.00	0.00	0.00	6800.00	t	2026-05-25	REC-1034	34
398	2	0.00	6800.00	0.00	0.00	13600.00	t	2026-05-25	REC-1034	34
399	3	0.00	6800.00	0.00	0.00	20400.00	t	2026-05-25	REC-1034	34
400	4	0.00	6800.00	0.00	0.00	0.00	f	\N		34
401	5	6800.00	6800.00	0.00	0.00	0.00	f	\N		34
402	6	13600.00	6800.00	0.00	0.00	0.00	f	\N		34
403	7	20400.00	6800.00	0.00	0.00	0.00	f	\N		34
404	8	27200.00	6800.00	0.00	0.00	0.00	f	\N		34
405	9	34000.00	6800.00	0.00	0.00	0.00	f	\N		34
406	10	40800.00	6800.00	0.00	0.00	0.00	f	\N		34
407	11	47600.00	6800.00	0.00	0.00	0.00	f	\N		34
408	12	54400.00	6800.00	0.00	0.00	0.00	f	\N		34
409	1	0.00	0.00	0.00	0.00	0.00	t	\N		35
410	2	0.00	0.00	0.00	0.00	0.00	t	\N		35
411	3	0.00	6000.00	0.00	0.00	6000.00	t	2026-03-27	REC-1035	35
412	4	0.00	6000.00	0.00	0.00	0.00	f	\N		35
413	5	6000.00	6000.00	0.00	0.00	0.00	f	\N		35
414	6	12000.00	6000.00	0.00	0.00	0.00	f	\N		35
415	7	18000.00	6000.00	0.00	0.00	0.00	f	\N		35
416	8	24000.00	6000.00	0.00	0.00	0.00	f	\N		35
417	9	30000.00	6000.00	0.00	0.00	0.00	f	\N		35
418	10	36000.00	6000.00	0.00	0.00	0.00	f	\N		35
419	11	42000.00	6000.00	0.00	0.00	0.00	f	\N		35
420	12	48000.00	6000.00	0.00	0.00	0.00	f	\N		35
421	1	0.00	0.00	0.00	0.00	0.00	t	\N		36
422	2	0.00	0.00	0.00	0.00	0.00	t	\N		36
423	3	0.00	0.00	0.00	0.00	0.00	t	\N		36
424	4	0.00	0.00	0.00	0.00	0.00	t	\N		36
425	5	0.00	0.00	0.00	0.00	0.00	t	\N		36
426	6	0.00	0.00	0.00	0.00	0.00	t	\N		36
427	7	0.00	0.00	0.00	0.00	0.00	t	\N		36
428	8	0.00	0.00	0.00	0.00	0.00	t	\N		36
429	9	0.00	0.00	0.00	0.00	0.00	t	\N		36
430	10	0.00	6200.00	0.00	0.00	6200.00	t	2026-04-01	REC-1036	36
431	11	0.00	6200.00	0.00	0.00	12400.00	t	2026-04-01	REC-1036	36
432	12	0.00	6200.00	0.00	0.00	0.00	f	\N		36
433	1	0.00	0.00	0.00	0.00	0.00	t	\N		37
434	2	0.00	0.00	0.00	0.00	0.00	t	\N		37
435	3	0.00	0.00	0.00	0.00	0.00	t	\N		37
436	4	0.00	0.00	0.00	0.00	0.00	t	\N		37
437	5	0.00	0.00	0.00	0.00	0.00	t	\N		37
438	6	0.00	0.00	0.00	0.00	0.00	t	\N		37
439	7	0.00	0.00	0.00	0.00	0.00	t	\N		37
440	8	0.00	0.00	0.00	0.00	0.00	t	\N		37
441	9	0.00	0.00	0.00	0.00	0.00	t	\N		37
442	10	0.00	0.00	0.00	0.00	0.00	t	\N		37
443	11	0.00	0.00	0.00	0.00	0.00	t	\N		37
444	12	0.00	2500.00	0.00	0.00	2500.00	t	2026-02-06	REC-1037	37
445	1	0.00	0.00	0.00	0.00	0.00	t	\N		38
446	2	0.00	0.00	0.00	0.00	0.00	t	\N		38
447	3	0.00	0.00	0.00	0.00	0.00	t	\N		38
448	4	0.00	0.00	0.00	0.00	0.00	t	\N		38
449	5	0.00	0.00	0.00	0.00	0.00	t	\N		38
450	6	0.00	0.00	0.00	0.00	0.00	t	\N		38
451	7	0.00	0.00	0.00	0.00	0.00	t	\N		38
452	8	0.00	0.00	0.00	0.00	0.00	t	\N		38
453	9	0.00	0.00	0.00	0.00	0.00	t	\N		38
454	10	0.00	0.00	0.00	0.00	0.00	t	\N		38
455	11	0.00	0.00	0.00	0.00	0.00	t	\N		38
456	12	0.00	2800.00	0.00	0.00	2800.00	t	2026-03-17	REC-1038	38
457	1	0.00	0.00	0.00	0.00	0.00	t	\N		39
458	2	0.00	0.00	0.00	0.00	0.00	t	\N		39
459	3	0.00	0.00	0.00	0.00	0.00	t	\N		39
460	4	0.00	0.00	0.00	0.00	0.00	t	\N		39
461	5	0.00	0.00	0.00	0.00	0.00	t	\N		39
462	6	0.00	0.00	0.00	0.00	0.00	t	\N		39
463	7	0.00	0.00	0.00	0.00	0.00	t	\N		39
464	8	0.00	0.00	0.00	0.00	0.00	t	\N		39
465	9	0.00	3000.00	0.00	0.00	3000.00	t	2026-03-08	REC-1039	39
466	10	0.00	3000.00	0.00	0.00	6000.00	t	2026-03-08	REC-1039	39
467	11	0.00	3000.00	0.00	0.00	0.00	f	\N		39
468	12	3000.00	3000.00	0.00	0.00	0.00	f	\N		39
469	1	0.00	0.00	0.00	0.00	0.00	t	\N		40
470	2	0.00	0.00	0.00	0.00	0.00	t	\N		40
471	3	0.00	0.00	0.00	0.00	0.00	t	\N		40
472	4	0.00	0.00	0.00	0.00	0.00	t	\N		40
473	5	0.00	0.00	0.00	0.00	0.00	t	\N		40
474	6	0.00	0.00	0.00	0.00	0.00	t	\N		40
475	7	0.00	3000.00	0.00	0.00	3000.00	t	2026-05-10	REC-1040	40
476	8	0.00	3000.00	0.00	0.00	6000.00	t	2026-05-10	REC-1040	40
477	9	0.00	3000.00	0.00	0.00	0.00	f	\N		40
478	10	3000.00	3000.00	0.00	0.00	0.00	f	\N		40
479	11	6000.00	3000.00	0.00	0.00	0.00	f	\N		40
480	12	9000.00	3000.00	0.00	0.00	0.00	f	\N		40
481	1	0.00	0.00	0.00	0.00	0.00	t	\N		41
482	2	0.00	0.00	0.00	0.00	0.00	t	\N		41
483	3	0.00	0.00	0.00	0.00	0.00	t	\N		41
484	4	0.00	0.00	0.00	0.00	0.00	t	\N		41
485	5	0.00	0.00	0.00	0.00	0.00	t	\N		41
486	6	0.00	0.00	0.00	0.00	0.00	t	\N		41
487	7	0.00	0.00	0.00	0.00	0.00	t	\N		41
488	8	0.00	0.00	0.00	0.00	0.00	t	\N		41
489	9	0.00	0.00	0.00	0.00	0.00	t	\N		41
490	10	0.00	3200.00	0.00	0.00	3200.00	t	2026-05-09	REC-1041	41
491	11	0.00	3200.00	0.00	0.00	0.00	f	\N		41
492	12	3200.00	3200.00	0.00	0.00	0.00	f	\N		41
493	1	0.00	0.00	0.00	0.00	0.00	t	\N		42
494	2	0.00	3200.00	0.00	0.00	3200.00	t	2026-01-02	REC-1042	42
495	3	0.00	3200.00	0.00	0.00	6400.00	t	2026-01-02	REC-1042	42
496	4	0.00	3200.00	0.00	0.00	0.00	f	\N		42
497	5	3200.00	3200.00	0.00	0.00	0.00	f	\N		42
498	6	6400.00	3200.00	0.00	0.00	0.00	f	\N		42
499	7	9600.00	3200.00	0.00	0.00	0.00	f	\N		42
500	8	12800.00	3200.00	0.00	0.00	0.00	f	\N		42
501	9	16000.00	3200.00	0.00	0.00	0.00	f	\N		42
502	10	19200.00	3200.00	0.00	0.00	0.00	f	\N		42
503	11	22400.00	3200.00	0.00	0.00	0.00	f	\N		42
504	12	25600.00	3200.00	0.00	0.00	0.00	f	\N		42
505	1	0.00	0.00	0.00	0.00	0.00	t	\N		43
506	2	0.00	3500.00	0.00	0.00	3500.00	t	2026-02-15	REC-1043	43
507	3	0.00	3500.00	0.00	0.00	7000.00	t	2026-02-15	REC-1043	43
508	4	0.00	3500.00	0.00	0.00	0.00	f	\N		43
509	5	3500.00	3500.00	0.00	0.00	0.00	f	\N		43
510	6	7000.00	3500.00	0.00	0.00	0.00	f	\N		43
511	7	10500.00	3500.00	0.00	0.00	0.00	f	\N		43
512	8	14000.00	3500.00	0.00	0.00	0.00	f	\N		43
513	9	17500.00	3500.00	0.00	0.00	0.00	f	\N		43
514	10	21000.00	3500.00	0.00	0.00	0.00	f	\N		43
515	11	24500.00	3500.00	0.00	0.00	0.00	f	\N		43
516	12	28000.00	3500.00	0.00	0.00	0.00	f	\N		43
517	1	0.00	0.00	0.00	0.00	0.00	t	\N		44
518	2	0.00	0.00	0.00	0.00	0.00	t	\N		44
519	3	0.00	0.00	0.00	0.00	0.00	t	\N		44
520	4	0.00	0.00	0.00	0.00	0.00	t	\N		44
521	5	0.00	0.00	0.00	0.00	0.00	t	\N		44
522	6	0.00	0.00	0.00	0.00	0.00	t	\N		44
523	7	0.00	0.00	0.00	0.00	0.00	t	\N		44
524	8	0.00	0.00	0.00	0.00	0.00	t	\N		44
525	9	0.00	0.00	0.00	0.00	0.00	t	\N		44
526	10	0.00	0.00	0.00	0.00	0.00	t	\N		44
527	11	0.00	0.00	0.00	0.00	0.00	t	\N		44
528	12	0.00	3800.00	0.00	0.00	3800.00	t	2026-07-12	REC-1044	44
529	1	0.00	0.00	0.00	0.00	0.00	t	\N		45
530	2	0.00	0.00	0.00	0.00	0.00	t	\N		45
531	3	0.00	0.00	0.00	0.00	0.00	t	\N		45
532	4	0.00	0.00	0.00	0.00	0.00	t	\N		45
533	5	0.00	0.00	0.00	0.00	0.00	t	\N		45
534	6	0.00	0.00	0.00	0.00	0.00	t	\N		45
535	7	0.00	0.00	0.00	0.00	0.00	t	\N		45
536	8	0.00	0.00	0.00	0.00	0.00	t	\N		45
537	9	0.00	0.00	0.00	0.00	0.00	t	\N		45
538	10	0.00	0.00	0.00	0.00	0.00	t	\N		45
539	11	0.00	4000.00	0.00	0.00	4000.00	t	2026-07-02	REC-1045	45
540	12	0.00	4000.00	0.00	0.00	8000.00	t	2026-07-02	REC-1045	45
541	1	0.00	0.00	0.00	0.00	0.00	t	\N		46
542	2	0.00	0.00	0.00	0.00	0.00	t	\N		46
543	3	0.00	0.00	0.00	0.00	0.00	t	\N		46
544	4	0.00	0.00	0.00	0.00	0.00	t	\N		46
545	5	0.00	0.00	0.00	0.00	0.00	t	\N		46
546	6	0.00	0.00	0.00	0.00	0.00	t	\N		46
547	7	0.00	0.00	0.00	0.00	0.00	t	\N		46
548	8	0.00	0.00	0.00	0.00	0.00	t	\N		46
549	9	0.00	0.00	0.00	0.00	0.00	t	\N		46
550	10	0.00	4200.00	0.00	0.00	4200.00	t	2026-02-05	REC-1046	46
551	11	0.00	4200.00	0.00	0.00	0.00	f	\N		46
552	12	4200.00	4200.00	0.00	0.00	0.00	f	\N		46
553	1	0.00	0.00	0.00	0.00	0.00	t	\N		47
554	2	0.00	0.00	0.00	0.00	0.00	t	\N		47
555	3	0.00	0.00	0.00	0.00	0.00	t	\N		47
556	4	0.00	4800.00	0.00	0.00	4800.00	t	2026-06-21	REC-1047	47
557	5	0.00	4800.00	0.00	0.00	9600.00	t	2026-06-21	REC-1047	47
558	6	0.00	4800.00	0.00	0.00	0.00	f	\N		47
559	7	4800.00	4800.00	0.00	0.00	0.00	f	\N		47
560	8	9600.00	4800.00	0.00	0.00	0.00	f	\N		47
561	9	14400.00	4800.00	0.00	0.00	0.00	f	\N		47
562	10	19200.00	4800.00	0.00	0.00	0.00	f	\N		47
563	11	24000.00	4800.00	0.00	0.00	0.00	f	\N		47
564	12	28800.00	4800.00	0.00	0.00	0.00	f	\N		47
565	1	0.00	0.00	0.00	0.00	0.00	t	\N		48
566	2	0.00	0.00	0.00	0.00	0.00	t	\N		48
567	3	0.00	0.00	0.00	0.00	0.00	t	\N		48
568	4	0.00	0.00	0.00	0.00	0.00	t	\N		48
569	5	0.00	0.00	0.00	0.00	0.00	t	\N		48
570	6	0.00	0.00	0.00	0.00	0.00	t	\N		48
571	7	0.00	0.00	0.00	0.00	0.00	t	\N		48
572	8	0.00	0.00	0.00	0.00	0.00	t	\N		48
573	9	0.00	0.00	0.00	0.00	0.00	t	\N		48
574	10	0.00	5000.00	0.00	0.00	5000.00	t	2026-06-04	REC-1048	48
575	11	0.00	5000.00	0.00	0.00	10000.00	t	2026-06-04	REC-1048	48
576	12	0.00	5000.00	0.00	0.00	0.00	f	\N		48
577	1	0.00	0.00	0.00	0.00	0.00	t	\N		49
578	2	0.00	0.00	0.00	0.00	0.00	t	\N		49
579	3	0.00	6500.00	0.00	0.00	6500.00	t	2026-06-04	REC-1049	49
580	4	0.00	6500.00	0.00	0.00	13000.00	t	2026-06-04	REC-1049	49
581	5	0.00	6500.00	0.00	0.00	19500.00	t	2026-06-04	REC-1049	49
582	6	0.00	6500.00	0.00	0.00	0.00	f	\N		49
583	7	6500.00	6500.00	0.00	0.00	0.00	f	\N		49
584	8	13000.00	6500.00	0.00	0.00	0.00	f	\N		49
585	9	19500.00	6500.00	0.00	0.00	0.00	f	\N		49
586	10	26000.00	6500.00	0.00	0.00	0.00	f	\N		49
587	11	32500.00	6500.00	0.00	0.00	0.00	f	\N		49
588	12	39000.00	6500.00	0.00	0.00	0.00	f	\N		49
589	1	0.00	0.00	0.00	0.00	0.00	t	\N		50
590	2	0.00	0.00	0.00	0.00	0.00	t	\N		50
591	3	0.00	0.00	0.00	0.00	0.00	t	\N		50
592	4	0.00	0.00	0.00	0.00	0.00	t	\N		50
593	5	0.00	0.00	0.00	0.00	0.00	t	\N		50
594	6	0.00	0.00	0.00	0.00	0.00	t	\N		50
595	7	0.00	0.00	0.00	0.00	0.00	t	\N		50
596	8	0.00	6800.00	0.00	0.00	6800.00	t	2026-07-08	REC-1050	50
597	9	0.00	6800.00	0.00	0.00	13600.00	t	2026-07-08	REC-1050	50
598	10	0.00	6800.00	0.00	0.00	0.00	f	\N		50
599	11	6800.00	6800.00	0.00	0.00	0.00	f	\N		50
600	12	13600.00	6800.00	0.00	0.00	0.00	f	\N		50
601	1	0.00	0.00	0.00	0.00	0.00	t	\N		51
602	2	0.00	0.00	0.00	0.00	0.00	t	\N		51
603	3	0.00	0.00	0.00	0.00	0.00	t	\N		51
604	4	0.00	0.00	0.00	0.00	0.00	t	\N		51
605	5	0.00	0.00	0.00	0.00	0.00	t	\N		51
606	6	0.00	0.00	0.00	0.00	0.00	t	\N		51
607	7	0.00	6500.00	0.00	0.00	0.00	f	\N		51
608	8	6500.00	6500.00	0.00	0.00	0.00	f	\N		51
609	9	13000.00	6500.00	0.00	0.00	0.00	f	\N		51
610	10	19500.00	6500.00	0.00	0.00	0.00	f	\N		51
611	11	26000.00	6500.00	0.00	0.00	0.00	f	\N		51
612	12	32500.00	6500.00	0.00	0.00	0.00	f	\N		51
613	1	0.00	0.00	0.00	0.00	0.00	t	\N		52
614	2	0.00	0.00	0.00	0.00	0.00	t	\N		52
615	3	0.00	0.00	0.00	0.00	0.00	t	\N		52
616	4	0.00	0.00	0.00	0.00	0.00	t	\N		52
617	5	0.00	0.00	0.00	0.00	0.00	t	\N		52
618	6	0.00	0.00	0.00	0.00	0.00	t	\N		52
619	7	0.00	0.00	0.00	0.00	0.00	t	\N		52
620	8	0.00	0.00	0.00	0.00	0.00	t	\N		52
621	9	0.00	0.00	0.00	0.00	0.00	t	\N		52
622	10	0.00	6800.00	0.00	0.00	0.00	f	\N		52
623	11	6800.00	6800.00	0.00	0.00	0.00	f	\N		52
624	12	13600.00	6800.00	0.00	0.00	0.00	f	\N		52
625	1	0.00	0.00	0.00	0.00	0.00	t	\N		53
626	2	0.00	0.00	0.00	0.00	0.00	t	\N		53
627	3	0.00	0.00	0.00	0.00	0.00	t	\N		53
628	4	0.00	0.00	0.00	0.00	0.00	t	\N		53
629	5	0.00	0.00	0.00	0.00	0.00	t	\N		53
630	6	0.00	0.00	0.00	0.00	0.00	t	\N		53
631	7	0.00	0.00	0.00	0.00	0.00	t	\N		53
632	8	0.00	0.00	0.00	0.00	0.00	t	\N		53
633	9	0.00	0.00	0.00	0.00	0.00	t	\N		53
634	10	0.00	0.00	0.00	0.00	0.00	t	\N		53
635	11	0.00	6000.00	0.00	0.00	0.00	f	\N		53
636	12	6000.00	6000.00	0.00	0.00	0.00	f	\N		53
637	1	0.00	0.00	0.00	0.00	0.00	t	\N		54
638	2	0.00	0.00	0.00	0.00	0.00	t	\N		54
639	3	0.00	6200.00	0.00	0.00	0.00	f	\N		54
640	4	6200.00	6200.00	0.00	0.00	0.00	f	\N		54
641	5	12400.00	6200.00	0.00	0.00	0.00	f	\N		54
642	6	18600.00	6200.00	0.00	0.00	0.00	f	\N		54
643	7	24800.00	6200.00	0.00	0.00	0.00	f	\N		54
644	8	31000.00	6200.00	0.00	0.00	0.00	f	\N		54
645	9	37200.00	6200.00	0.00	0.00	0.00	f	\N		54
646	10	43400.00	6200.00	0.00	0.00	0.00	f	\N		54
647	11	49600.00	6200.00	0.00	0.00	0.00	f	\N		54
648	12	55800.00	6200.00	0.00	0.00	0.00	f	\N		54
649	1	0.00	0.00	0.00	0.00	0.00	t	\N		55
650	2	0.00	0.00	0.00	0.00	0.00	t	\N		55
651	3	0.00	0.00	0.00	0.00	0.00	t	\N		55
652	4	0.00	0.00	0.00	0.00	0.00	t	\N		55
653	5	0.00	0.00	0.00	0.00	0.00	t	\N		55
654	6	0.00	2500.00	0.00	0.00	0.00	f	\N		55
655	7	2500.00	2500.00	0.00	0.00	0.00	f	\N		55
656	8	5000.00	2500.00	0.00	0.00	0.00	f	\N		55
657	9	7500.00	2500.00	0.00	0.00	0.00	f	\N		55
658	10	10000.00	2500.00	0.00	0.00	0.00	f	\N		55
659	11	12500.00	2500.00	0.00	0.00	0.00	f	\N		55
660	12	15000.00	2500.00	0.00	0.00	0.00	f	\N		55
661	1	0.00	0.00	0.00	0.00	0.00	t	\N		56
662	2	0.00	0.00	0.00	0.00	0.00	t	\N		56
663	3	0.00	2800.00	0.00	0.00	0.00	f	\N		56
664	4	2800.00	2800.00	0.00	0.00	0.00	f	\N		56
665	5	5600.00	2800.00	0.00	0.00	0.00	f	\N		56
666	6	8400.00	2800.00	0.00	0.00	0.00	f	\N		56
667	7	11200.00	2800.00	0.00	0.00	0.00	f	\N		56
668	8	14000.00	2800.00	0.00	0.00	0.00	f	\N		56
669	9	16800.00	2800.00	0.00	0.00	0.00	f	\N		56
670	10	19600.00	2800.00	0.00	0.00	0.00	f	\N		56
671	11	22400.00	2800.00	0.00	0.00	0.00	f	\N		56
672	12	25200.00	2800.00	0.00	0.00	0.00	f	\N		56
685	1	0.00	3000.00	0.00	0.00	0.00	f	\N		58
686	2	3000.00	3000.00	0.00	0.00	0.00	f	\N		58
687	3	6000.00	3000.00	0.00	0.00	0.00	f	\N		58
688	4	9000.00	3000.00	0.00	0.00	0.00	f	\N		58
689	5	12000.00	3000.00	0.00	0.00	0.00	f	\N		58
690	6	15000.00	3000.00	0.00	0.00	0.00	f	\N		58
691	7	18000.00	3000.00	0.00	0.00	0.00	f	\N		58
692	8	21000.00	3000.00	0.00	0.00	0.00	f	\N		58
693	9	24000.00	3000.00	0.00	0.00	0.00	f	\N		58
694	10	27000.00	3000.00	0.00	0.00	0.00	f	\N		58
695	11	30000.00	3000.00	0.00	0.00	0.00	f	\N		58
696	12	33000.00	3000.00	0.00	0.00	0.00	f	\N		58
697	1	0.00	0.00	0.00	0.00	0.00	t	\N		59
698	2	0.00	0.00	0.00	0.00	0.00	t	\N		59
699	3	0.00	0.00	0.00	0.00	0.00	t	\N		59
700	4	0.00	0.00	0.00	0.00	0.00	t	\N		59
701	5	0.00	0.00	0.00	0.00	0.00	t	\N		59
702	6	0.00	0.00	0.00	0.00	0.00	t	\N		59
703	7	0.00	0.00	0.00	0.00	0.00	t	\N		59
704	8	0.00	3200.00	0.00	0.00	0.00	f	\N		59
705	9	3200.00	3200.00	0.00	0.00	0.00	f	\N		59
706	10	6400.00	3200.00	0.00	0.00	0.00	f	\N		59
707	11	9600.00	3200.00	0.00	0.00	0.00	f	\N		59
708	12	12800.00	3200.00	0.00	0.00	0.00	f	\N		59
709	1	0.00	0.00	0.00	0.00	0.00	t	\N		60
710	2	0.00	0.00	0.00	0.00	0.00	t	\N		60
711	3	0.00	0.00	0.00	0.00	0.00	t	\N		60
712	4	0.00	0.00	0.00	0.00	0.00	t	\N		60
713	5	0.00	0.00	0.00	0.00	0.00	t	\N		60
714	6	0.00	0.00	0.00	0.00	0.00	t	\N		60
715	7	0.00	0.00	0.00	0.00	0.00	t	\N		60
716	8	0.00	0.00	0.00	0.00	0.00	t	\N		60
717	9	0.00	0.00	0.00	0.00	0.00	t	\N		60
718	10	0.00	0.00	0.00	0.00	0.00	t	\N		60
719	11	0.00	0.00	0.00	0.00	0.00	t	\N		60
720	12	0.00	3200.00	0.00	0.00	0.00	f	\N		60
721	1	0.00	0.00	0.00	0.00	0.00	t	\N		61
722	2	0.00	0.00	0.00	0.00	0.00	t	\N		61
723	3	0.00	0.00	0.00	0.00	0.00	t	\N		61
724	4	0.00	0.00	0.00	0.00	0.00	t	\N		61
725	5	0.00	0.00	0.00	0.00	0.00	t	\N		61
726	6	0.00	0.00	0.00	0.00	0.00	t	\N		61
727	7	0.00	3500.00	0.00	0.00	0.00	f	\N		61
728	8	3500.00	3500.00	0.00	0.00	0.00	f	\N		61
729	9	7000.00	3500.00	0.00	0.00	0.00	f	\N		61
730	10	10500.00	3500.00	0.00	0.00	0.00	f	\N		61
731	11	14000.00	3500.00	0.00	0.00	0.00	f	\N		61
732	12	17500.00	3500.00	0.00	0.00	0.00	f	\N		61
733	1	0.00	0.00	0.00	0.00	0.00	t	\N		62
734	2	0.00	0.00	0.00	0.00	0.00	t	\N		62
735	3	0.00	0.00	0.00	0.00	0.00	t	\N		62
736	4	0.00	0.00	0.00	0.00	0.00	t	\N		62
737	5	0.00	0.00	0.00	0.00	0.00	t	\N		62
738	6	0.00	0.00	0.00	0.00	0.00	t	\N		62
739	7	0.00	0.00	0.00	0.00	0.00	t	\N		62
740	8	0.00	3800.00	0.00	0.00	0.00	f	\N		62
741	9	3800.00	3800.00	0.00	0.00	0.00	f	\N		62
742	10	7600.00	3800.00	0.00	0.00	0.00	f	\N		62
743	11	11400.00	3800.00	0.00	0.00	0.00	f	\N		62
744	12	15200.00	3800.00	0.00	0.00	0.00	f	\N		62
745	1	0.00	0.00	0.00	0.00	0.00	t	\N		63
746	2	0.00	0.00	0.00	0.00	0.00	t	\N		63
747	3	0.00	0.00	0.00	0.00	0.00	t	\N		63
748	4	0.00	0.00	0.00	0.00	0.00	t	\N		63
749	5	0.00	0.00	0.00	0.00	0.00	t	\N		63
750	6	0.00	0.00	0.00	0.00	0.00	t	\N		63
751	7	0.00	0.00	0.00	0.00	0.00	t	\N		63
752	8	0.00	0.00	0.00	0.00	0.00	t	\N		63
753	9	0.00	0.00	0.00	0.00	0.00	t	\N		63
754	10	0.00	0.00	0.00	0.00	0.00	t	\N		63
755	11	0.00	4000.00	0.00	0.00	0.00	f	\N		63
756	12	4000.00	4000.00	0.00	0.00	0.00	f	\N		63
757	1	0.00	0.00	0.00	0.00	0.00	t	\N		64
758	2	0.00	0.00	0.00	0.00	0.00	t	\N		64
759	3	0.00	0.00	0.00	0.00	0.00	t	\N		64
760	4	0.00	0.00	0.00	0.00	0.00	t	\N		64
761	5	0.00	0.00	0.00	0.00	0.00	t	\N		64
762	6	0.00	0.00	0.00	0.00	0.00	t	\N		64
763	7	0.00	4200.00	0.00	0.00	0.00	f	\N		64
764	8	4200.00	4200.00	0.00	0.00	0.00	f	\N		64
765	9	8400.00	4200.00	0.00	0.00	0.00	f	\N		64
766	10	12600.00	4200.00	0.00	0.00	0.00	f	\N		64
767	11	16800.00	4200.00	0.00	0.00	0.00	f	\N		64
768	12	21000.00	4200.00	0.00	0.00	0.00	f	\N		64
769	1	0.00	0.00	0.00	0.00	0.00	t	\N		65
770	2	0.00	0.00	0.00	0.00	0.00	t	\N		65
771	3	0.00	0.00	0.00	0.00	0.00	t	\N		65
772	4	0.00	0.00	0.00	0.00	0.00	t	\N		65
773	5	0.00	0.00	0.00	0.00	0.00	t	\N		65
774	6	0.00	4800.00	0.00	0.00	0.00	f	\N		65
775	7	4800.00	4800.00	0.00	0.00	0.00	f	\N		65
776	8	9600.00	4800.00	0.00	0.00	0.00	f	\N		65
777	9	14400.00	4800.00	0.00	0.00	0.00	f	\N		65
778	10	19200.00	4800.00	0.00	0.00	0.00	f	\N		65
779	11	24000.00	4800.00	0.00	0.00	0.00	f	\N		65
780	12	28800.00	4800.00	0.00	0.00	0.00	f	\N		65
781	1	0.00	0.00	0.00	0.00	0.00	t	\N		66
782	2	0.00	0.00	0.00	0.00	0.00	t	\N		66
783	3	0.00	0.00	0.00	0.00	0.00	t	\N		66
784	4	0.00	0.00	0.00	0.00	0.00	t	\N		66
785	5	0.00	0.00	0.00	0.00	0.00	t	\N		66
786	6	0.00	0.00	0.00	0.00	0.00	t	\N		66
787	7	0.00	0.00	0.00	0.00	0.00	t	\N		66
788	8	0.00	5000.00	0.00	0.00	0.00	f	\N		66
789	9	5000.00	5000.00	0.00	0.00	0.00	f	\N		66
790	10	10000.00	5000.00	0.00	0.00	0.00	f	\N		66
791	11	15000.00	5000.00	0.00	0.00	0.00	f	\N		66
792	12	20000.00	5000.00	0.00	0.00	0.00	f	\N		66
793	1	0.00	0.00	0.00	0.00	0.00	t	\N		67
794	2	0.00	0.00	0.00	0.00	0.00	t	\N		67
795	3	0.00	0.00	0.00	0.00	0.00	t	\N		67
796	4	0.00	6500.00	0.00	0.00	0.00	f	\N		67
797	5	6500.00	6500.00	0.00	0.00	0.00	f	\N		67
798	6	13000.00	6500.00	0.00	0.00	0.00	f	\N		67
799	7	19500.00	6500.00	0.00	0.00	0.00	f	\N		67
800	8	26000.00	6500.00	0.00	0.00	0.00	f	\N		67
801	9	32500.00	6500.00	0.00	0.00	0.00	f	\N		67
802	10	39000.00	6500.00	0.00	0.00	0.00	f	\N		67
803	11	45500.00	6500.00	0.00	0.00	0.00	f	\N		67
804	12	52000.00	6500.00	0.00	0.00	0.00	f	\N		67
805	1	0.00	0.00	0.00	0.00	0.00	t	\N		68
806	2	0.00	0.00	0.00	0.00	0.00	t	\N		68
807	3	0.00	0.00	0.00	0.00	0.00	t	\N		68
808	4	0.00	0.00	0.00	0.00	0.00	t	\N		68
809	5	0.00	0.00	0.00	0.00	0.00	t	\N		68
810	6	0.00	0.00	0.00	0.00	0.00	t	\N		68
811	7	0.00	6800.00	0.00	0.00	0.00	f	\N		68
812	8	6800.00	6800.00	0.00	0.00	0.00	f	\N		68
813	9	13600.00	6800.00	0.00	0.00	0.00	f	\N		68
814	10	20400.00	6800.00	0.00	0.00	0.00	f	\N		68
815	11	27200.00	6800.00	0.00	0.00	0.00	f	\N		68
816	12	34000.00	6800.00	0.00	0.00	0.00	f	\N		68
817	1	0.00	0.00	0.00	0.00	0.00	t	\N		69
818	2	0.00	0.00	0.00	0.00	0.00	t	\N		69
819	3	0.00	0.00	0.00	0.00	0.00	t	\N		69
820	4	0.00	6500.00	0.00	0.00	0.00	f	\N		69
821	5	6500.00	6500.00	0.00	0.00	0.00	f	\N		69
822	6	13000.00	6500.00	0.00	0.00	0.00	f	\N		69
823	7	19500.00	6500.00	0.00	0.00	0.00	f	\N		69
824	8	26000.00	6500.00	0.00	0.00	0.00	f	\N		69
825	9	32500.00	6500.00	0.00	0.00	0.00	f	\N		69
826	10	39000.00	6500.00	0.00	0.00	0.00	f	\N		69
827	11	45500.00	6500.00	0.00	0.00	0.00	f	\N		69
828	12	52000.00	6500.00	0.00	0.00	0.00	f	\N		69
829	1	0.00	6800.00	0.00	0.00	0.00	f	\N		70
830	2	6800.00	6800.00	0.00	0.00	0.00	f	\N		70
831	3	13600.00	6800.00	0.00	0.00	0.00	f	\N		70
832	4	20400.00	6800.00	0.00	0.00	0.00	f	\N		70
833	5	27200.00	6800.00	0.00	0.00	0.00	f	\N		70
834	6	34000.00	6800.00	0.00	0.00	0.00	f	\N		70
835	7	40800.00	6800.00	0.00	0.00	0.00	f	\N		70
836	8	47600.00	6800.00	0.00	0.00	0.00	f	\N		70
837	9	54400.00	6800.00	0.00	0.00	0.00	f	\N		70
838	10	61200.00	6800.00	0.00	0.00	0.00	f	\N		70
839	11	68000.00	6800.00	0.00	0.00	0.00	f	\N		70
840	12	74800.00	6800.00	0.00	0.00	0.00	f	\N		70
841	1	0.00	0.00	0.00	0.00	0.00	t	\N		71
842	2	0.00	0.00	0.00	0.00	0.00	t	\N		71
843	3	0.00	0.00	0.00	0.00	0.00	t	\N		71
844	4	0.00	0.00	0.00	0.00	0.00	t	\N		71
845	5	0.00	0.00	0.00	0.00	0.00	t	\N		71
846	6	0.00	0.00	0.00	0.00	0.00	t	\N		71
847	7	0.00	0.00	0.00	0.00	0.00	t	\N		71
848	8	0.00	0.00	0.00	0.00	0.00	t	\N		71
849	9	0.00	0.00	0.00	0.00	0.00	t	\N		71
850	10	0.00	0.00	0.00	0.00	0.00	t	\N		71
851	11	0.00	6000.00	0.00	0.00	0.00	f	\N		71
852	12	6000.00	6000.00	0.00	0.00	0.00	f	\N		71
853	1	0.00	0.00	0.00	0.00	0.00	t	\N		72
854	2	0.00	0.00	0.00	0.00	0.00	t	\N		72
855	3	0.00	6200.00	0.00	0.00	0.00	f	\N		72
856	4	6200.00	6200.00	0.00	0.00	0.00	f	\N		72
857	5	12400.00	6200.00	0.00	0.00	0.00	f	\N		72
858	6	18600.00	6200.00	0.00	0.00	0.00	f	\N		72
859	7	24800.00	6200.00	0.00	0.00	0.00	f	\N		72
860	8	31000.00	6200.00	0.00	0.00	0.00	f	\N		72
861	9	37200.00	6200.00	0.00	0.00	0.00	f	\N		72
862	10	43400.00	6200.00	0.00	0.00	0.00	f	\N		72
863	11	49600.00	6200.00	0.00	0.00	0.00	f	\N		72
864	12	55800.00	6200.00	0.00	0.00	0.00	f	\N		72
865	1	0.00	0.00	0.00	0.00	0.00	t	\N		73
866	2	0.00	0.00	0.00	0.00	0.00	t	\N		73
867	3	0.00	0.00	0.00	0.00	0.00	t	\N		73
868	4	0.00	0.00	0.00	0.00	0.00	t	\N		73
869	5	0.00	0.00	0.00	0.00	0.00	t	\N		73
870	6	0.00	0.00	0.00	0.00	0.00	t	\N		73
871	7	0.00	0.00	0.00	0.00	0.00	t	\N		73
872	8	0.00	2500.00	0.00	0.00	0.00	f	\N		73
873	9	2500.00	2500.00	0.00	0.00	0.00	f	\N		73
874	10	5000.00	2500.00	0.00	0.00	0.00	f	\N		73
875	11	7500.00	2500.00	0.00	0.00	0.00	f	\N		73
876	12	10000.00	2500.00	0.00	0.00	0.00	f	\N		73
877	1	0.00	0.00	0.00	0.00	0.00	t	\N		74
878	2	0.00	0.00	0.00	0.00	0.00	t	\N		74
879	3	0.00	0.00	0.00	0.00	0.00	t	\N		74
880	4	0.00	0.00	0.00	0.00	0.00	t	\N		74
881	5	0.00	0.00	0.00	0.00	0.00	t	\N		74
882	6	0.00	0.00	0.00	0.00	0.00	t	\N		74
883	7	0.00	0.00	0.00	0.00	0.00	t	\N		74
884	8	0.00	0.00	0.00	0.00	0.00	t	\N		74
885	9	0.00	0.00	0.00	0.00	0.00	t	\N		74
886	10	0.00	2800.00	0.00	0.00	0.00	f	\N		74
887	11	2800.00	2800.00	0.00	0.00	0.00	f	\N		74
888	12	5600.00	2800.00	0.00	0.00	0.00	f	\N		74
889	1	0.00	0.00	0.00	0.00	0.00	t	\N		75
890	2	0.00	0.00	0.00	0.00	0.00	t	\N		75
891	3	0.00	0.00	0.00	0.00	0.00	t	\N		75
892	4	0.00	0.00	0.00	0.00	0.00	t	\N		75
893	5	0.00	0.00	0.00	0.00	0.00	t	\N		75
894	6	0.00	0.00	0.00	0.00	0.00	t	\N		75
895	7	0.00	0.00	0.00	0.00	0.00	t	\N		75
896	8	0.00	0.00	0.00	0.00	0.00	t	\N		75
897	9	0.00	0.00	0.00	0.00	0.00	t	\N		75
898	10	0.00	0.00	0.00	0.00	0.00	t	\N		75
899	11	0.00	3000.00	0.00	0.00	0.00	f	\N		75
900	12	3000.00	3000.00	0.00	0.00	0.00	f	\N		75
\.


--
-- Data for Name: school_academicsession; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.school_academicsession (id, name, start_date, end_date, is_active) FROM stdin;
1	2024-2025	2024-04-01	2025-03-31	f
2	2025-2026	2025-04-01	2026-03-31	t
3	2026-2027	2026-04-01	2027-03-31	f
\.


--
-- Data for Name: school_classlevel; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.school_classlevel (id, name, level, monthly_fee) FROM stdin;
1	Nursery	Prep	2500.00
2	Prep	Prep	2800.00
3	Class 1	Primary	3000.00
4	Class 2	Primary	3000.00
5	Class 3	Primary	3200.00
6	Class 4	Primary	3200.00
7	Class 5	Primary	3500.00
8	Class 6	Middle	3800.00
9	Class 7	Middle	4000.00
10	Class 8	Middle	4200.00
11	Class 9	High	4800.00
12	Class 10	High	5000.00
13	1st Year Pre-Medical	Higher Secondary	6500.00
14	2nd Year Pre-Medical	Higher Secondary	6800.00
15	1st Year Pre-Engineering	Higher Secondary	6500.00
16	2nd Year Pre-Engineering	Higher Secondary	6800.00
17	ICS 1st Year	Higher Secondary	6000.00
18	ICS 2nd Year	Higher Secondary	6200.00
\.


--
-- Data for Name: school_schoolsetting; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.school_schoolsetting (id, name, address, logo, contact, academic_session_format, receipt_no_prefix, last_receipt_no) FROM stdin;
1	Kohisar Model School & College	Qalagay, Tehsil Kabal, District Swat, Khyber Pakhtunkhwa	school_logos/logo.png	+92 344 9631323 / +92 345 3407095	2025-2026	REC-	1058
\.


--
-- Data for Name: school_section; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.school_section (id, name, class_teacher, class_level_id) FROM stdin;
28	B	Teacher of 2nd Year Pre-Medical-B	14
29	A	Teacher of 1st Year Pre-Engineering-A	15
30	B	Teacher of 1st Year Pre-Engineering-B	15
31	A	Teacher of 2nd Year Pre-Engineering-A	16
32	B	Teacher of 2nd Year Pre-Engineering-B	16
33	A	Teacher of ICS 1st Year-A	17
34	B	Teacher of ICS 1st Year-B	17
35	A	Teacher of ICS 2nd Year-A	18
36	B	Teacher of ICS 2nd Year-B	18
1	A	Teacher of Nursery-A	1
2	B	Teacher of Nursery-B	1
3	A	Teacher of Prep-A	2
4	B	Teacher of Prep-B	2
5	A	Teacher of Class 1-A	3
6	B	Teacher of Class 1-B	3
7	A	Teacher of Class 2-A	4
8	B	Teacher of Class 2-B	4
9	A	Teacher of Class 3-A	5
10	B	Teacher of Class 3-B	5
11	A	Teacher of Class 4-A	6
12	B	Teacher of Class 4-B	6
13	A	Teacher of Class 5-A	7
14	B	Teacher of Class 5-B	7
15	A	Teacher of Class 6-A	8
16	B	Teacher of Class 6-B	8
17	A	Teacher of Class 7-A	9
18	B	Teacher of Class 7-B	9
19	A	Teacher of Class 8-A	10
20	B	Teacher of Class 8-B	10
21	A	Teacher of Class 9-A	11
22	B	Teacher of Class 9-B	11
23	A	Teacher of Class 10-A	12
24	B	Teacher of Class 10-B	12
25	A	Teacher of 1st Year Pre-Medical-A	13
26	B	Teacher of 1st Year Pre-Medical-B	13
27	A	Teacher of 2nd Year Pre-Medical-A	14
\.


--
-- Data for Name: students_familyhousehold; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.students_familyhousehold (id, family_id, father_guardian_name, contact_number, address) FROM stdin;
48	FAM-0048	Kashan Zada	03001505236	Barikot Central, Swat KPK
1	FAM-0001	Moiz Ahmad	03125044035	Ghalegay Near Rock Carving, Swat
2	FAM-0002	Salman Hussain	03314274603	Kabal Main Road, Swat
3	FAM-0003	Bilal Swati	03127943151	Main Bazaar Qalagay, Swat
4	FAM-0004	Zeeshan Khan	03006673636	Barikot Central, Swat KPK
5	FAM-0005	Danish Hussain	03121094346	Matta Road, Swat KPK
6	FAM-0006	Shahzad Zada	03127716005	Main Bazaar Qalagay, Swat
7	FAM-0007	Waleed Rehman	03009563869	Qalagay, Tehsil Barikot, District Swat
8	FAM-0008	Noman Ahmad	03335998432	Qalagay, Tehsil Barikot, District Swat
9	FAM-0009	Sameer Gul	03456959248	Ghalegay Near Rock Carving, Swat
10	FAM-0010	Bilal Yousafzai	03339616961	Qalagay, Tehsil Barikot, District Swat
11	FAM-0011	Hassan Gul	03333263936	Ghalegay Near Rock Carving, Swat
12	FAM-0012	Sameer Jan	03126463428	Qalagay, Tehsil Barikot, District Swat
13	FAM-0013	Mustafa Zada	03006645222	Matta Road, Swat KPK
14	FAM-0014	Salman Ali	03339374775	Qalagay, Tehsil Barikot, District Swat
15	FAM-0015	Ibrahim Hussain	03124586126	Main Bazaar Qalagay, Swat
16	FAM-0016	Hazrat Hussain	03477401410	Khwazakhela Bazaar, Swat
17	FAM-0017	Abdullah Shah	03338069925	Main Bazaar Qalagay, Swat
18	FAM-0018	Junaid Khan	03475411262	Mingora City, Swat KPK
19	FAM-0019	Sardar Jan	03317605367	Mingora City, Swat KPK
20	FAM-0020	Zubair Yousafzai	03452054720	Matta Road, Swat KPK
21	FAM-0021	Haris Swati	03454724050	Kabal Main Road, Swat
22	FAM-0022	Moiz Khan	03476098559	Barikot Central, Swat KPK
23	FAM-0023	Kashan Ali	03335853034	Khwazakhela Bazaar, Swat
24	FAM-0024	Haris Rehman	03336741092	Matta Road, Swat KPK
26	FAM-0026	Zubair Khan	0345-1234567	Mingora Swat
27	FAM-0027	Faizan Hussain	03452374466	Matta Road, Swat KPK
28	FAM-0028	Moiz Ali	03007154376	Khwazakhela Bazaar, Swat
29	FAM-0029	Zubair Hussain	03451716150	Kabal Main Road, Swat
30	FAM-0030	Aman Hussain	03453356781	Main Bazaar Qalagay, Swat
31	FAM-0031	Hazrat Gul	03008431022	Matta Road, Swat KPK
32	FAM-0032	Haris Khan	03128286395	Matta Road, Swat KPK
33	FAM-0033	Adil Swati	03004831340	Main Bazaar Qalagay, Swat
34	FAM-0034	Rizwan Shah	03455325233	Saidu Sharif Near Central Hospital, Swat
35	FAM-0035	Muhammad Ahmad	03312252193	Mingora City, Swat KPK
36	FAM-0036	Sami Ahmad	03123862752	Khwazakhela Bazaar, Swat
37	FAM-0037	Haris Yousafzai	03477012725	Saidu Sharif Near Central Hospital, Swat
38	FAM-0038	Hazrat Shah	03457911487	Ghalegay Near Rock Carving, Swat
39	FAM-0039	Waleed Shah	03338961647	Matta Road, Swat KPK
40	FAM-0040	Hassan Hussain	03459723063	Matta Road, Swat KPK
41	FAM-0041	Gulzar Gul	03459346045	Khwazakhela Bazaar, Swat
42	FAM-0042	Abdullah Bibi	03331010017	Khwazakhela Bazaar, Swat
43	FAM-0043	Junaid Hussain	03335159745	Saidu Sharif Near Central Hospital, Swat
44	FAM-0044	Sardar Hussain	03124287387	Main Bazaar Qalagay, Swat
45	FAM-0045	Sami Shah	03335251884	Barikot Central, Swat KPK
46	FAM-0046	Taimur Ali	03331535098	Barikot Central, Swat KPK
47	FAM-0047	Zain Bibi	03312543849	Qalagay, Tehsil Barikot, District Swat
25	FAM-0025	Tariq Hussain	03127794449	Main Bazaar Qalagay, Swat
\.


--
-- Data for Name: students_promotionhistory; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.students_promotionhistory (id, session, promotion_date, from_class_id, from_section_id, to_class_id, to_section_id, student_id) FROM stdin;
1	2026-2027	2026-09-05	3	5	6	12	3
2	2026-2027	2026-09-05	3	5	6	12	21
3	2026-2027	2026-09-05	3	5	6	12	39
4	2026-2027	2026-09-05	3	5	6	12	57
\.


--
-- Data for Name: students_student; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.students_student (id, admission_no, admission_date, full_name, father_name, dob, gender, tribe_caste, father_occupation, residence, contact_number, profile_picture, status, inactive_date, remarks, withdrawal_date, class_at_withdrawal, arrears_at_withdrawal, current_class_id, current_section_id, family_id) FROM stdin;
152	SSA26005	2026-09-09	Kamal Zada	Zaman Zada	2020-02-11	Male	Yousafzai	Business / Govt Service	Qalagay	03477251244	students/Gemini_Generated_Image_1ucpwj1ucpwj1ucp.jfif	Active	\N	need flexable	\N		0.00	1	3	\N
160	1076	2026-09-09	Hussain	Ali Jan	2026-09-09	Male						Active	\N		\N		0.00	15	1	\N
2	1002	2025-04-02	Mustafa Jan	Salman Hussain	2020-06-23	Male	Yousafzai	Business / Govt Service	Kabal Main Road, Swat	03472685102		Active	\N		\N		0.00	2	3	2
4	1004	2025-06-26	Sana Khan	Zeeshan Khan	2018-09-17	Female	Yousafzai	Business / Govt Service	Barikot Central, Swat KPK	03123975407		Active	\N		\N		0.00	4	7	4
5	1005	2024-01-08	Moiz Zada	Danish Hussain	2017-07-13	Male	Yousafzai	Business / Govt Service	Matta Road, Swat KPK	03471634287		Active	\N		\N		0.00	5	9	5
6	1006	2024-09-08	Talha Yousafzai	Shahzad Zada	2016-07-26	Male	Yousafzai	Business / Govt Service	Main Bazaar Qalagay, Swat	03121739719		Active	\N		\N		0.00	6	11	6
7	1007	2023-10-23	Bakht Yousafzai	Waleed Rehman	2015-01-04	Male	Yousafzai	Business / Govt Service	Qalagay, Tehsil Barikot, District Swat	03312410160		Active	\N		\N		0.00	7	13	7
9	1009	2024-11-20	Junaid Shah	Sameer Gul	2013-06-12	Male	Yousafzai	Business / Govt Service	Ghalegay Near Rock Carving, Swat	03009741121		Active	\N		\N		0.00	9	17	9
10	1010	2022-08-04	Shaukat Rehman	Bilal Yousafzai	2012-03-06	Male	Yousafzai	Business / Govt Service	Qalagay, Tehsil Barikot, District Swat	03454268890		Active	\N		\N		0.00	10	19	10
11	1011	2025-10-25	Shoaib Shah	Hassan Gul	2011-11-22	Male	Yousafzai	Business / Govt Service	Ghalegay Near Rock Carving, Swat	03318127731		Active	\N		\N		0.00	11	21	11
12	1012	2024-09-07	Ayesha Khan	Sameer Jan	2010-01-23	Female	Yousafzai	Business / Govt Service	Qalagay, Tehsil Barikot, District Swat	03007871656		Active	\N		\N		0.00	12	23	12
13	1013	2023-02-19	Salman Gul	Mustafa Zada	2009-06-05	Male	Yousafzai	Business / Govt Service	Matta Road, Swat KPK	03477968362		Active	\N		\N		0.00	13	25	13
3	1003	2024-03-10	Hamza Ahmad	Bilal Swati	2019-04-14	Male	Yousafzai	Business / Govt Service	Main Bazaar Qalagay, Swat	03129686589		Active	\N		\N		0.00	6	12	3
14	1014	2022-12-02	Sameer Hussain	Salman Ali	2022-05-20	Male	Yousafzai	Business / Govt Service	Qalagay, Tehsil Barikot, District Swat	03128364582		Active	\N		\N		0.00	14	27	14
15	1015	2025-08-27	Farhan Ali	Ibrahim Hussain	2021-11-12	Male	Yousafzai	Business / Govt Service	Main Bazaar Qalagay, Swat	03455412181		Active	\N		\N		0.00	15	29	15
16	1016	2025-03-19	Zainab Khan	Hazrat Hussain	2020-06-22	Female	Yousafzai	Business / Govt Service	Khwazakhela Bazaar, Swat	03332833453		Active	\N		\N		0.00	16	31	16
17	1017	2025-07-02	Bilal Bibi	Abdullah Shah	2019-08-23	Male	Yousafzai	Business / Govt Service	Main Bazaar Qalagay, Swat	03451595833		Active	\N		\N		0.00	17	33	17
18	1018	2023-12-21	Rizwan Yousafzai	Junaid Khan	2018-11-18	Male	Yousafzai	Business / Govt Service	Mingora City, Swat KPK	03477225778		Active	\N		\N		0.00	18	35	18
53	1053	2022-11-16	Aman Ali	Zubair Hussain	2011-07-02	Male	Yousafzai	Business / Govt Service	Kabal Main Road, Swat	03451716150		Active	\N		\N		0.00	17	33	\N
161	1077	2026-09-09	Umar Zada	Zafar Zada	2026-09-09	Male						Active	\N		\N		0.00	1	1	\N
8	1008	2023-04-02	Fatima Bibi	Noman Ahmad	2014-02-09	Female	Yousafzai	Business / Govt Service	Qalagay, Tehsil Barikot, District Swat	03337750494	students/boy__image_6.jpg	Active	\N		\N		0.00	8	15	8
1	1001	2022-08-27	Zubair Gul	Moiz Ahmad	2021-11-01	Male	Yousafzai	Business / Govt Service	Ghalegay Near Rock Carving, Swat	03002512326		Active	\N		\N		0.00	1	1	1
162	1078	2026-09-09	New Student Test	Mr Guardian	2015-01-01	Male						Active	\N		\N		0.00	15	29	\N
163	1099	2026-09-11	Kamal Ali	Zaf	2002-09-11	Male	Y	job less	qalagay	4535345345		Active	\N	from ppmsq	\N		0.00	11	22	\N
19	1019	2023-08-23	Abdullah Rehman	Sardar Jan	2017-07-14	Male	Yousafzai	Business / Govt Service	Mingora City, Swat KPK	03007454119		Active	\N		\N		0.00	1	1	19
20	1020	2025-11-09	Hira Bibi	Zubair Yousafzai	2016-02-25	Female	Yousafzai	Business / Govt Service	Matta Road, Swat KPK	03337270825		Active	\N		\N		0.00	2	3	20
22	1022	2024-12-08	Farhan Ahmad	Moiz Khan	2014-09-26	Male	Yousafzai	Business / Govt Service	Barikot Central, Swat KPK	03335512732		Active	\N		\N		0.00	4	7	22
23	1023	2024-01-19	Abdullah Ali	Kashan Ali	2013-12-19	Male	Yousafzai	Business / Govt Service	Khwazakhela Bazaar, Swat	03004020484		Active	\N		\N		0.00	5	9	23
24	1024	2025-07-24	Mahnoor Khan	Haris Rehman	2012-12-07	Female	Yousafzai	Business / Govt Service	Matta Road, Swat KPK	03313892607		Active	\N		\N		0.00	6	11	24
25	1025	2024-12-12	Shoaib Swati	Tariq Hussain	2011-10-27	Male	Yousafzai	Business / Govt Service	Main Bazaar Qalagay, Swat	03003033612		Active	\N		\N		0.00	7	13	25
26	1026	2023-12-22	Danish Ali	Moiz Ahmad	2010-07-01	Male	Yousafzai	Business / Govt Service	Ghalegay Near Rock Carving, Swat	03333845733		Active	\N		\N		0.00	8	15	1
27	1027	2022-09-17	Danish Hussain	Salman Hussain	2009-09-09	Male	Yousafzai	Business / Govt Service	Kabal Main Road, Swat	03335220484		Active	\N		\N		0.00	9	17	2
28	1028	2024-08-11	Mehwish Khan	Bilal Swati	2022-07-22	Female	Yousafzai	Business / Govt Service	Main Bazaar Qalagay, Swat	03459690395		Active	\N		\N		0.00	10	19	3
29	1029	2024-10-18	Shahzad Bibi	Zeeshan Khan	2021-06-16	Male	Yousafzai	Business / Govt Service	Barikot Central, Swat KPK	03121750777		Active	\N		\N		0.00	11	21	4
30	1030	2024-06-14	Aman Jan	Danish Hussain	2020-11-17	Male	Yousafzai	Business / Govt Service	Matta Road, Swat KPK	03129811012		Active	\N		\N		0.00	12	23	5
31	1031	2022-11-22	Talha Bibi	Shahzad Zada	2019-07-25	Male	Yousafzai	Business / Govt Service	Main Bazaar Qalagay, Swat	03008681550		Active	\N		\N		0.00	13	25	6
32	1032	2023-06-11	Mehwish Khan	Waleed Rehman	2018-07-07	Female	Yousafzai	Business / Govt Service	Qalagay, Tehsil Barikot, District Swat	03479912190		Active	\N		\N		0.00	14	27	7
33	1033	2024-04-10	Sami Bibi	Noman Ahmad	2017-12-16	Male	Yousafzai	Business / Govt Service	Qalagay, Tehsil Barikot, District Swat	03311749557		Active	\N		\N		0.00	15	29	8
34	1034	2022-01-13	Junaid Yousafzai	Sameer Gul	2016-05-11	Male	Yousafzai	Business / Govt Service	Ghalegay Near Rock Carving, Swat	03472732546		Active	\N		\N		0.00	16	31	9
35	1035	2023-03-17	Zubair Hussain	Bilal Yousafzai	2015-03-17	Male	Yousafzai	Business / Govt Service	Qalagay, Tehsil Barikot, District Swat	03331281179		Active	\N		\N		0.00	17	33	10
36	1036	2023-10-05	Sidra Bibi	Hassan Gul	2014-02-15	Female	Yousafzai	Business / Govt Service	Ghalegay Near Rock Carving, Swat	03455813377		Active	\N		\N		0.00	18	35	11
37	1037	2025-12-06	Zubair Swati	Sameer Jan	2013-09-02	Male	Yousafzai	Business / Govt Service	Qalagay, Tehsil Barikot, District Swat	03126315733		Active	\N		\N		0.00	1	1	12
38	1038	2024-12-07	Ali Gul	Mustafa Zada	2012-12-18	Male	Yousafzai	Business / Govt Service	Matta Road, Swat KPK	03458755200		Active	\N		\N		0.00	2	3	13
40	1040	2023-07-19	Maryam Khan	Ibrahim Hussain	2010-01-19	Female	Yousafzai	Business / Govt Service	Main Bazaar Qalagay, Swat	03474523976		Active	\N		\N		0.00	4	7	15
41	1041	2025-10-09	Mustafa Swati	Hazrat Hussain	2009-11-12	Male	Yousafzai	Business / Govt Service	Khwazakhela Bazaar, Swat	03336521668		Active	\N		\N		0.00	5	9	16
42	1042	2025-02-22	Shahzad Rehman	Abdullah Shah	2022-05-08	Male	Yousafzai	Business / Govt Service	Main Bazaar Qalagay, Swat	03319459473		Active	\N		\N		0.00	6	11	17
43	1043	2023-02-22	Adil Yousafzai	Junaid Khan	2021-10-13	Male	Yousafzai	Business / Govt Service	Mingora City, Swat KPK	03126190072		Active	\N		\N		0.00	7	13	18
44	1044	2023-12-17	Hafsa Bibi	Sardar Jan	2020-10-08	Female	Yousafzai	Business / Govt Service	Mingora City, Swat KPK	03471457751		Active	\N		\N		0.00	8	15	19
45	1045	2025-11-11	Junaid Ahmad	Zubair Yousafzai	2019-07-25	Male	Yousafzai	Business / Govt Service	Matta Road, Swat KPK	03312096943		Active	\N		\N		0.00	9	17	20
46	1046	2024-10-21	Noman Ahmad	Haris Swati	2018-01-23	Male	Yousafzai	Business / Govt Service	Kabal Main Road, Swat	03339785492		Active	\N		\N		0.00	10	19	21
47	1047	2023-04-27	Junaid Khan	Moiz Khan	2017-09-14	Male	Yousafzai	Business / Govt Service	Barikot Central, Swat KPK	03478939971		Active	\N		\N		0.00	11	21	22
48	1048	2023-10-14	Sana Khan	Kashan Ali	2016-07-17	Female	Yousafzai	Business / Govt Service	Khwazakhela Bazaar, Swat	03336105253		Active	\N		\N		0.00	12	23	23
49	1049	2023-03-28	Usman Khan	Haris Rehman	2015-09-11	Male	Yousafzai	Business / Govt Service	Matta Road, Swat KPK	03456504151		Active	\N		\N		0.00	13	25	24
50	1050	2022-08-19	Tariq Ahmad	Tariq Hussain	2014-11-13	Male	Yousafzai	Business / Govt Service	Main Bazaar Qalagay, Swat	03459246033		Active	\N		\N		0.00	14	27	25
51	1051	2025-07-03	Saad Ali	Faizan Hussain	2013-12-07	Male	Yousafzai	Business / Govt Service	Matta Road, Swat KPK	03452374466		Active	\N		\N		0.00	15	29	\N
52	1052	2022-10-01	Laiba Khan	Moiz Ali	2012-04-12	Female	Yousafzai	Business / Govt Service	Khwazakhela Bazaar, Swat	03007154376		Active	\N		\N		0.00	16	31	\N
54	1054	2023-03-28	Haris Ahmad	Aman Hussain	2010-03-07	Male	Yousafzai	Business / Govt Service	Main Bazaar Qalagay, Swat	03453356781		Active	\N		\N		0.00	18	35	\N
55	1055	2024-06-28	Umar Ali	Hazrat Gul	2009-04-26	Male	Yousafzai	Business / Govt Service	Matta Road, Swat KPK	03008431022		Active	\N		\N		0.00	1	1	\N
56	1056	2023-03-02	Maryam Khan	Haris Khan	2022-11-06	Female	Yousafzai	Business / Govt Service	Matta Road, Swat KPK	03128286395		Active	\N		\N		0.00	2	3	\N
58	1058	2025-01-09	Gulzar Rehman	Adil Swati	2020-03-22	Male	Yousafzai	Business / Govt Service	Main Bazaar Qalagay, Swat	03004831340		Active	\N		\N		0.00	4	7	\N
59	1059	2023-08-15	Sami Jan	Rizwan Shah	2019-12-06	Male	Yousafzai	Business / Govt Service	Saidu Sharif Near Central Hospital, Swat	03455325233		Active	\N		\N		0.00	5	9	\N
60	1060	2024-12-27	Aiman Gul	Muhammad Ahmad	2018-08-03	Female	Yousafzai	Business / Govt Service	Mingora City, Swat KPK	03312252193		Active	\N		\N		0.00	6	11	\N
61	1061	2025-07-23	Fazal Khan	Sami Ahmad	2017-02-17	Male	Yousafzai	Business / Govt Service	Khwazakhela Bazaar, Swat	03123862752		Active	\N		\N		0.00	7	13	\N
62	1062	2023-08-21	Moiz Khan	Haris Yousafzai	2016-08-21	Male	Yousafzai	Business / Govt Service	Saidu Sharif Near Central Hospital, Swat	03477012725		Active	\N		\N		0.00	8	15	\N
63	1063	2024-11-24	Shaukat Jan	Haris Yousafzai	2015-11-07	Male	Yousafzai	Business / Govt Service	Mingora City, Swat KPK	03335635048		Active	\N		\N		0.00	9	17	\N
64	1064	2025-07-22	Zainab Bibi	Hazrat Shah	2014-09-13	Female	Yousafzai	Business / Govt Service	Ghalegay Near Rock Carving, Swat	03457911487		Active	\N		\N		0.00	10	19	\N
65	1065	2024-06-28	Hassan Jan	Waleed Shah	2013-05-05	Male	Yousafzai	Business / Govt Service	Matta Road, Swat KPK	03338961647		Active	\N		\N		0.00	11	21	\N
66	1066	2022-08-20	Rizwan Ali	Hassan Hussain	2012-01-06	Male	Yousafzai	Business / Govt Service	Matta Road, Swat KPK	03459723063		Active	\N		\N		0.00	12	23	\N
67	1067	2023-04-03	Adil Ali	Zubair Khan	2011-07-20	Male	Yousafzai	Business / Govt Service	Khwazakhela Bazaar, Swat	03333766857		Active	\N		\N		0.00	13	25	\N
68	1068	2023-07-20	Zainab Khan	Gulzar Gul	2010-01-21	Female	Yousafzai	Business / Govt Service	Khwazakhela Bazaar, Swat	03459346045		Active	\N		\N		0.00	14	27	\N
69	1069	2025-04-15	Ali Hussain	Abdullah Bibi	2009-06-02	Male	Yousafzai	Business / Govt Service	Khwazakhela Bazaar, Swat	03331010017		Active	\N		\N		0.00	15	29	\N
70	1070	2022-01-04	Hamza Hussain	Junaid Hussain	2022-09-12	Male	Yousafzai	Business / Govt Service	Saidu Sharif Near Central Hospital, Swat	03335159745		Active	\N		\N		0.00	16	31	\N
71	1071	2022-11-19	Farooq Zada	Sardar Hussain	2021-04-20	Male	Yousafzai	Business / Govt Service	Main Bazaar Qalagay, Swat	03124287387		Active	\N		\N		0.00	17	33	\N
72	1072	2022-03-25	Maryam Gul	Sami Shah	2020-06-06	Female	Yousafzai	Business / Govt Service	Barikot Central, Swat KPK	03335251884		Active	\N		\N		0.00	18	35	\N
73	1073	2024-08-09	Farooq Khan	Taimur Ali	2019-10-15	Male	Yousafzai	Business / Govt Service	Barikot Central, Swat KPK	03331535098		Active	\N		\N		0.00	1	1	\N
74	1074	2023-10-21	Talha Zada	Zain Bibi	2018-11-09	Male	Yousafzai	Business / Govt Service	Qalagay, Tehsil Barikot, District Swat	03312543849		Inactive	\N		\N		0.00	2	3	\N
75	1075	2025-11-28	Hazrat Khan	Kashan Zada	2017-03-05	Male	Yousafzai	Business / Govt Service	Barikot Central, Swat KPK	03001505236		Withdrawn	\N		2026-06-15	Class 1 - A	0.00	3	5	\N
21	1021	2025-03-24	Danish Yousafzai	Haris Swati	2015-11-17	Male	Yousafzai	Business / Govt Service	Kabal Main Road, Swat	03457711360		Active	\N		\N		0.00	6	12	21
39	1039	2024-09-14	Usman Zada	Salman Ali	2011-08-02	Male	Yousafzai	Business / Govt Service	Qalagay, Tehsil Barikot, District Swat	03477325447		Active	\N		\N		0.00	6	12	14
57	1057	2022-12-22	Umar Jan	Mustafa Zada	2021-03-05	Male	Yousafzai	Business / Govt Service	Mingora City, Swat KPK	03008217701	students/boy_image_5.jpg	Active	\N		\N		0.00	6	12	\N
\.


--
-- Data for Name: teachers_monthlysalarybill; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.teachers_monthlysalarybill (id, month, year, base_pay, days_present, allowances, deductions, is_paid, payment_date, voucher_no, teacher_id, paid_amount) FROM stdin;
243	9	2026	68000.00	30	22000.00	0.00	f	\N		3	0.00
244	9	2026	68000.00	30	22000.00	0.00	f	\N		4	0.00
245	9	2026	68000.00	30	22000.00	0.00	f	\N		5	0.00
246	9	2026	68000.00	30	22000.00	0.00	f	\N		6	0.00
247	9	2026	52000.00	30	17000.00	0.00	f	\N		7	0.00
248	9	2026	52000.00	30	17000.00	0.00	f	\N		8	0.00
249	9	2026	52000.00	30	17000.00	0.00	f	\N		9	0.00
250	9	2026	38000.00	30	13000.00	0.00	f	\N		10	0.00
251	9	2026	38000.00	30	13000.00	0.00	f	\N		11	0.00
252	9	2026	38000.00	30	13000.00	0.00	f	\N		12	0.00
253	9	2026	28000.00	30	9000.00	0.00	f	\N		13	0.00
254	9	2026	28000.00	30	9000.00	0.00	f	\N		14	0.00
255	9	2026	38000.00	30	13000.00	0.00	f	\N		15	0.00
256	9	2026	38000.00	30	13000.00	0.00	f	\N		16	0.00
257	9	2026	45000.00	30	13000.00	0.00	f	\N		17	0.00
258	9	2026	45000.00	30	13000.00	0.00	f	\N		18	0.00
259	9	2026	68000.00	30	22000.00	0.00	f	\N		19	0.00
260	9	2026	68000.00	30	22000.00	0.00	f	\N		20	0.00
261	9	2026	68000.00	30	22000.00	0.00	f	\N		21	0.00
262	9	2026	68000.00	30	22000.00	0.00	f	\N		22	0.00
264	9	2026	68000.00	30	22000.00	0.00	f	\N		24	0.00
265	9	2026	52000.00	30	17000.00	0.00	f	\N		25	0.00
266	9	2026	52000.00	30	17000.00	0.00	f	\N		26	0.00
267	9	2026	52000.00	30	17000.00	0.00	f	\N		27	0.00
268	9	2026	38000.00	30	13000.00	0.00	f	\N		28	0.00
269	9	2026	38000.00	30	13000.00	0.00	f	\N		29	0.00
270	9	2026	38000.00	30	13000.00	0.00	f	\N		30	0.00
271	9	2026	28000.00	30	9000.00	0.00	f	\N		31	0.00
272	9	2026	28000.00	30	9000.00	0.00	f	\N		32	0.00
273	9	2026	38000.00	30	13000.00	0.00	f	\N		33	0.00
274	9	2026	38000.00	30	13000.00	0.00	f	\N		34	0.00
275	9	2026	45000.00	30	13000.00	0.00	f	\N		35	0.00
276	9	2026	45000.00	30	13000.00	0.00	f	\N		36	0.00
277	9	2026	68000.00	30	22000.00	0.00	f	\N		37	0.00
278	9	2026	68000.00	30	22000.00	0.00	f	\N		38	0.00
279	9	2026	68000.00	30	22000.00	0.00	f	\N		39	0.00
280	9	2026	68000.00	30	22000.00	0.00	f	\N		40	0.00
281	9	2026	68000.00	30	22000.00	0.00	f	\N		41	0.00
282	9	2026	68000.00	30	22000.00	0.00	f	\N		42	0.00
283	9	2026	52000.00	30	17000.00	0.00	f	\N		43	0.00
284	9	2026	52000.00	30	17000.00	0.00	f	\N		44	0.00
285	9	2026	52000.00	30	17000.00	0.00	f	\N		45	0.00
286	9	2026	38000.00	30	13000.00	0.00	f	\N		46	0.00
287	9	2026	38000.00	30	13000.00	0.00	f	\N		47	0.00
288	9	2026	38000.00	30	13000.00	0.00	f	\N		48	0.00
289	9	2026	28000.00	30	9000.00	0.00	f	\N		49	0.00
290	9	2026	28000.00	30	9000.00	0.00	f	\N		50	0.00
241	9	2026	68000.00	30	22000.00	0.00	f	2026-09-05	20005	1	0.00
263	9	2026	68000.00	23	21999.99	0.00	t	2026-09-04	1000	23	89999.99
312	8	2026	28000.00	30	0.00	0.00	t	2026-09-04	2000	56	28000.00
242	9	2026	68000.00	30	22000.00	6000.00	t	2026-09-12		2	84000.00
333	9	2026	68000.00	30	22000.00	0.00	f	\N		59	0.00
119	4	2026	38000.00	30	13000.00	0.00	t	2026-04-28	VCH-2026-04-029	29	0.00
291	5	2026	28000.00	30	9000.00	0.00	f	\N		31	0.00
292	5	2026	28000.00	30	9000.00	0.00	f	\N		32	0.00
293	5	2026	38000.00	30	13000.00	0.00	f	\N		33	0.00
294	5	2026	38000.00	30	13000.00	0.00	f	\N		34	0.00
295	5	2026	45000.00	30	13000.00	0.00	f	\N		35	0.00
296	5	2026	45000.00	30	13000.00	0.00	f	\N		36	0.00
297	5	2026	68000.00	30	22000.00	0.00	f	\N		37	0.00
298	5	2026	68000.00	30	22000.00	0.00	f	\N		38	0.00
299	5	2026	68000.00	30	22000.00	0.00	f	\N		39	0.00
300	5	2026	68000.00	30	22000.00	0.00	f	\N		40	0.00
301	5	2026	68000.00	30	22000.00	0.00	f	\N		41	0.00
302	5	2026	68000.00	30	22000.00	0.00	f	\N		42	0.00
303	5	2026	52000.00	30	17000.00	0.00	f	\N		43	0.00
304	5	2026	52000.00	30	17000.00	0.00	f	\N		44	0.00
305	5	2026	52000.00	30	17000.00	0.00	f	\N		45	0.00
306	5	2026	38000.00	30	13000.00	0.00	f	\N		46	0.00
307	5	2026	38000.00	30	13000.00	0.00	f	\N		47	0.00
308	5	2026	38000.00	30	13000.00	0.00	f	\N		48	0.00
309	5	2026	28000.00	30	9000.00	0.00	f	\N		49	0.00
310	5	2026	28000.00	30	9000.00	0.00	f	\N		50	0.00
1	1	2026	68000.00	30	22000.00	0.00	t	2026-01-28	VCH-2026-01-001	1	0.00
311	9	2026	28000.00	18	0.00	0.00	t	2026-09-04		56	28000.00
2	1	2026	68000.00	30	22000.00	0.00	t	2026-01-28	VCH-2026-01-002	2	0.00
3	1	2026	68000.00	30	22000.00	0.00	t	2026-01-28	VCH-2026-01-003	3	0.00
4	1	2026	68000.00	30	22000.00	0.00	t	2026-01-28	VCH-2026-01-004	4	0.00
5	1	2026	68000.00	30	22000.00	0.00	t	2026-01-28	VCH-2026-01-005	5	0.00
6	1	2026	68000.00	30	22000.00	0.00	t	2026-01-28	VCH-2026-01-006	6	0.00
7	1	2026	52000.00	30	17000.00	0.00	t	2026-01-28	VCH-2026-01-007	7	0.00
8	1	2026	52000.00	30	17000.00	0.00	t	2026-01-28	VCH-2026-01-008	8	0.00
9	1	2026	52000.00	30	17000.00	0.00	t	2026-01-28	VCH-2026-01-009	9	0.00
10	1	2026	38000.00	30	13000.00	0.00	t	2026-01-28	VCH-2026-01-010	10	0.00
11	1	2026	38000.00	30	13000.00	0.00	t	2026-01-28	VCH-2026-01-011	11	0.00
12	1	2026	38000.00	30	13000.00	0.00	t	2026-01-28	VCH-2026-01-012	12	0.00
13	1	2026	28000.00	30	9000.00	0.00	t	2026-01-28	VCH-2026-01-013	13	0.00
14	1	2026	28000.00	30	9000.00	0.00	t	2026-01-28	VCH-2026-01-014	14	0.00
15	1	2026	38000.00	30	13000.00	0.00	t	2026-01-28	VCH-2026-01-015	15	0.00
16	1	2026	38000.00	30	13000.00	0.00	t	2026-01-28	VCH-2026-01-016	16	0.00
17	1	2026	45000.00	30	13000.00	0.00	t	2026-01-28	VCH-2026-01-017	17	0.00
18	1	2026	45000.00	30	13000.00	0.00	t	2026-01-28	VCH-2026-01-018	18	0.00
19	1	2026	68000.00	30	22000.00	0.00	t	2026-01-28	VCH-2026-01-019	19	0.00
20	1	2026	68000.00	30	22000.00	0.00	t	2026-01-28	VCH-2026-01-020	20	0.00
21	1	2026	68000.00	30	22000.00	0.00	t	2026-01-28	VCH-2026-01-021	21	0.00
22	1	2026	68000.00	30	22000.00	0.00	t	2026-01-28	VCH-2026-01-022	22	0.00
23	1	2026	68000.00	30	22000.00	0.00	t	2026-01-28	VCH-2026-01-023	23	0.00
24	1	2026	68000.00	30	22000.00	0.00	t	2026-01-28	VCH-2026-01-024	24	0.00
25	1	2026	52000.00	30	17000.00	0.00	t	2026-01-28	VCH-2026-01-025	25	0.00
26	1	2026	52000.00	30	17000.00	0.00	t	2026-01-28	VCH-2026-01-026	26	0.00
27	1	2026	52000.00	30	17000.00	0.00	t	2026-01-28	VCH-2026-01-027	27	0.00
28	1	2026	38000.00	30	13000.00	0.00	t	2026-01-28	VCH-2026-01-028	28	0.00
29	1	2026	38000.00	30	13000.00	0.00	t	2026-01-28	VCH-2026-01-029	29	0.00
30	1	2026	38000.00	30	13000.00	0.00	t	2026-01-28	VCH-2026-01-030	30	0.00
31	2	2026	68000.00	30	22000.00	0.00	t	2026-02-28	VCH-2026-02-001	1	0.00
32	2	2026	68000.00	30	22000.00	0.00	t	2026-02-28	VCH-2026-02-002	2	0.00
33	2	2026	68000.00	30	22000.00	0.00	t	2026-02-28	VCH-2026-02-003	3	0.00
34	2	2026	68000.00	30	22000.00	0.00	t	2026-02-28	VCH-2026-02-004	4	0.00
35	2	2026	68000.00	30	22000.00	0.00	t	2026-02-28	VCH-2026-02-005	5	0.00
36	2	2026	68000.00	30	22000.00	0.00	t	2026-02-28	VCH-2026-02-006	6	0.00
37	2	2026	52000.00	30	17000.00	0.00	t	2026-02-28	VCH-2026-02-007	7	0.00
38	2	2026	52000.00	30	17000.00	0.00	t	2026-02-28	VCH-2026-02-008	8	0.00
39	2	2026	52000.00	30	17000.00	0.00	t	2026-02-28	VCH-2026-02-009	9	0.00
40	2	2026	38000.00	30	13000.00	0.00	t	2026-02-28	VCH-2026-02-010	10	0.00
41	2	2026	38000.00	30	13000.00	0.00	t	2026-02-28	VCH-2026-02-011	11	0.00
42	2	2026	38000.00	30	13000.00	0.00	t	2026-02-28	VCH-2026-02-012	12	0.00
43	2	2026	28000.00	30	9000.00	0.00	t	2026-02-28	VCH-2026-02-013	13	0.00
44	2	2026	28000.00	30	9000.00	0.00	t	2026-02-28	VCH-2026-02-014	14	0.00
45	2	2026	38000.00	30	13000.00	0.00	t	2026-02-28	VCH-2026-02-015	15	0.00
46	2	2026	38000.00	30	13000.00	0.00	t	2026-02-28	VCH-2026-02-016	16	0.00
47	2	2026	45000.00	30	13000.00	0.00	t	2026-02-28	VCH-2026-02-017	17	0.00
48	2	2026	45000.00	30	13000.00	0.00	t	2026-02-28	VCH-2026-02-018	18	0.00
49	2	2026	68000.00	30	22000.00	0.00	t	2026-02-28	VCH-2026-02-019	19	0.00
50	2	2026	68000.00	30	22000.00	0.00	t	2026-02-28	VCH-2026-02-020	20	0.00
51	2	2026	68000.00	30	22000.00	0.00	t	2026-02-28	VCH-2026-02-021	21	0.00
52	2	2026	68000.00	30	22000.00	0.00	t	2026-02-28	VCH-2026-02-022	22	0.00
53	2	2026	68000.00	30	22000.00	0.00	t	2026-02-28	VCH-2026-02-023	23	0.00
54	2	2026	68000.00	30	22000.00	0.00	t	2026-02-28	VCH-2026-02-024	24	0.00
55	2	2026	52000.00	30	17000.00	0.00	t	2026-02-28	VCH-2026-02-025	25	0.00
56	2	2026	52000.00	30	17000.00	0.00	t	2026-02-28	VCH-2026-02-026	26	0.00
57	2	2026	52000.00	30	17000.00	0.00	t	2026-02-28	VCH-2026-02-027	27	0.00
58	2	2026	38000.00	30	13000.00	0.00	t	2026-02-28	VCH-2026-02-028	28	0.00
59	2	2026	38000.00	30	13000.00	0.00	t	2026-02-28	VCH-2026-02-029	29	0.00
60	2	2026	38000.00	30	13000.00	0.00	t	2026-02-28	VCH-2026-02-030	30	0.00
61	3	2026	68000.00	30	22000.00	0.00	t	2026-03-28	VCH-2026-03-001	1	0.00
62	3	2026	68000.00	30	22000.00	0.00	t	2026-03-28	VCH-2026-03-002	2	0.00
63	3	2026	68000.00	30	22000.00	0.00	t	2026-03-28	VCH-2026-03-003	3	0.00
64	3	2026	68000.00	30	22000.00	0.00	t	2026-03-28	VCH-2026-03-004	4	0.00
65	3	2026	68000.00	30	22000.00	0.00	t	2026-03-28	VCH-2026-03-005	5	0.00
66	3	2026	68000.00	30	22000.00	0.00	t	2026-03-28	VCH-2026-03-006	6	0.00
67	3	2026	52000.00	30	17000.00	0.00	t	2026-03-28	VCH-2026-03-007	7	0.00
68	3	2026	52000.00	30	17000.00	0.00	t	2026-03-28	VCH-2026-03-008	8	0.00
69	3	2026	52000.00	30	17000.00	0.00	t	2026-03-28	VCH-2026-03-009	9	0.00
70	3	2026	38000.00	30	13000.00	0.00	t	2026-03-28	VCH-2026-03-010	10	0.00
71	3	2026	38000.00	30	13000.00	0.00	t	2026-03-28	VCH-2026-03-011	11	0.00
72	3	2026	38000.00	30	13000.00	0.00	t	2026-03-28	VCH-2026-03-012	12	0.00
73	3	2026	28000.00	30	9000.00	0.00	t	2026-03-28	VCH-2026-03-013	13	0.00
74	3	2026	28000.00	30	9000.00	0.00	t	2026-03-28	VCH-2026-03-014	14	0.00
75	3	2026	38000.00	30	13000.00	0.00	t	2026-03-28	VCH-2026-03-015	15	0.00
76	3	2026	38000.00	30	13000.00	0.00	t	2026-03-28	VCH-2026-03-016	16	0.00
77	3	2026	45000.00	30	13000.00	0.00	t	2026-03-28	VCH-2026-03-017	17	0.00
78	3	2026	45000.00	30	13000.00	0.00	t	2026-03-28	VCH-2026-03-018	18	0.00
79	3	2026	68000.00	30	22000.00	0.00	t	2026-03-28	VCH-2026-03-019	19	0.00
80	3	2026	68000.00	30	22000.00	0.00	t	2026-03-28	VCH-2026-03-020	20	0.00
81	3	2026	68000.00	30	22000.00	0.00	t	2026-03-28	VCH-2026-03-021	21	0.00
82	3	2026	68000.00	30	22000.00	0.00	t	2026-03-28	VCH-2026-03-022	22	0.00
83	3	2026	68000.00	30	22000.00	0.00	t	2026-03-28	VCH-2026-03-023	23	0.00
84	3	2026	68000.00	30	22000.00	0.00	t	2026-03-28	VCH-2026-03-024	24	0.00
85	3	2026	52000.00	30	17000.00	0.00	t	2026-03-28	VCH-2026-03-025	25	0.00
86	3	2026	52000.00	30	17000.00	0.00	t	2026-03-28	VCH-2026-03-026	26	0.00
87	3	2026	52000.00	30	17000.00	0.00	t	2026-03-28	VCH-2026-03-027	27	0.00
88	3	2026	38000.00	30	13000.00	0.00	t	2026-03-28	VCH-2026-03-028	28	0.00
89	3	2026	38000.00	30	13000.00	0.00	t	2026-03-28	VCH-2026-03-029	29	0.00
90	3	2026	38000.00	30	13000.00	0.00	t	2026-03-28	VCH-2026-03-030	30	0.00
91	4	2026	68000.00	30	22000.00	0.00	t	2026-04-28	VCH-2026-04-001	1	0.00
92	4	2026	68000.00	30	22000.00	0.00	t	2026-04-28	VCH-2026-04-002	2	0.00
93	4	2026	68000.00	30	22000.00	0.00	t	2026-04-28	VCH-2026-04-003	3	0.00
94	4	2026	68000.00	30	22000.00	0.00	t	2026-04-28	VCH-2026-04-004	4	0.00
95	4	2026	68000.00	30	22000.00	0.00	t	2026-04-28	VCH-2026-04-005	5	0.00
96	4	2026	68000.00	30	22000.00	0.00	t	2026-04-28	VCH-2026-04-006	6	0.00
97	4	2026	52000.00	30	17000.00	0.00	t	2026-04-28	VCH-2026-04-007	7	0.00
98	4	2026	52000.00	30	17000.00	0.00	t	2026-04-28	VCH-2026-04-008	8	0.00
99	4	2026	52000.00	30	17000.00	0.00	t	2026-04-28	VCH-2026-04-009	9	0.00
100	4	2026	38000.00	30	13000.00	0.00	t	2026-04-28	VCH-2026-04-010	10	0.00
101	4	2026	38000.00	30	13000.00	0.00	t	2026-04-28	VCH-2026-04-011	11	0.00
102	4	2026	38000.00	30	13000.00	0.00	t	2026-04-28	VCH-2026-04-012	12	0.00
103	4	2026	28000.00	30	9000.00	0.00	t	2026-04-28	VCH-2026-04-013	13	0.00
104	4	2026	28000.00	30	9000.00	0.00	t	2026-04-28	VCH-2026-04-014	14	0.00
105	4	2026	38000.00	30	13000.00	0.00	t	2026-04-28	VCH-2026-04-015	15	0.00
106	4	2026	38000.00	30	13000.00	0.00	t	2026-04-28	VCH-2026-04-016	16	0.00
107	4	2026	45000.00	30	13000.00	0.00	t	2026-04-28	VCH-2026-04-017	17	0.00
108	4	2026	45000.00	30	13000.00	0.00	t	2026-04-28	VCH-2026-04-018	18	0.00
109	4	2026	68000.00	30	22000.00	0.00	t	2026-04-28	VCH-2026-04-019	19	0.00
110	4	2026	68000.00	30	22000.00	0.00	t	2026-04-28	VCH-2026-04-020	20	0.00
111	4	2026	68000.00	30	22000.00	0.00	t	2026-04-28	VCH-2026-04-021	21	0.00
112	4	2026	68000.00	30	22000.00	0.00	t	2026-04-28	VCH-2026-04-022	22	0.00
113	4	2026	68000.00	30	22000.00	0.00	t	2026-04-28	VCH-2026-04-023	23	0.00
114	4	2026	68000.00	30	22000.00	0.00	t	2026-04-28	VCH-2026-04-024	24	0.00
115	4	2026	52000.00	30	17000.00	0.00	t	2026-04-28	VCH-2026-04-025	25	0.00
116	4	2026	52000.00	30	17000.00	0.00	t	2026-04-28	VCH-2026-04-026	26	0.00
117	4	2026	52000.00	30	17000.00	0.00	t	2026-04-28	VCH-2026-04-027	27	0.00
118	4	2026	38000.00	30	13000.00	0.00	t	2026-04-28	VCH-2026-04-028	28	0.00
120	4	2026	38000.00	30	13000.00	0.00	t	2026-04-28	VCH-2026-04-030	30	0.00
121	5	2026	68000.00	30	22000.00	0.00	t	2026-05-28	VCH-2026-05-001	1	0.00
122	5	2026	68000.00	30	22000.00	0.00	t	2026-05-28	VCH-2026-05-002	2	0.00
123	5	2026	68000.00	30	22000.00	0.00	t	2026-05-28	VCH-2026-05-003	3	0.00
124	5	2026	68000.00	30	22000.00	0.00	t	2026-05-28	VCH-2026-05-004	4	0.00
125	5	2026	68000.00	30	22000.00	0.00	t	2026-05-28	VCH-2026-05-005	5	0.00
126	5	2026	68000.00	30	22000.00	0.00	t	2026-05-28	VCH-2026-05-006	6	0.00
127	5	2026	52000.00	30	17000.00	0.00	t	2026-05-28	VCH-2026-05-007	7	0.00
128	5	2026	52000.00	30	17000.00	0.00	t	2026-05-28	VCH-2026-05-008	8	0.00
129	5	2026	52000.00	30	17000.00	0.00	t	2026-05-28	VCH-2026-05-009	9	0.00
130	5	2026	38000.00	30	13000.00	0.00	t	2026-05-28	VCH-2026-05-010	10	0.00
131	5	2026	38000.00	30	13000.00	0.00	t	2026-05-28	VCH-2026-05-011	11	0.00
132	5	2026	38000.00	30	13000.00	0.00	t	2026-05-28	VCH-2026-05-012	12	0.00
133	5	2026	28000.00	30	9000.00	0.00	t	2026-05-28	VCH-2026-05-013	13	0.00
134	5	2026	28000.00	30	9000.00	0.00	t	2026-05-28	VCH-2026-05-014	14	0.00
135	5	2026	38000.00	30	13000.00	0.00	t	2026-05-28	VCH-2026-05-015	15	0.00
136	5	2026	38000.00	30	13000.00	0.00	t	2026-05-28	VCH-2026-05-016	16	0.00
137	5	2026	45000.00	30	13000.00	0.00	t	2026-05-28	VCH-2026-05-017	17	0.00
138	5	2026	45000.00	30	13000.00	0.00	t	2026-05-28	VCH-2026-05-018	18	0.00
139	5	2026	68000.00	30	22000.00	0.00	t	2026-05-28	VCH-2026-05-019	19	0.00
140	5	2026	68000.00	30	22000.00	0.00	t	2026-05-28	VCH-2026-05-020	20	0.00
141	5	2026	68000.00	30	22000.00	0.00	t	2026-05-28	VCH-2026-05-021	21	0.00
142	5	2026	68000.00	30	22000.00	0.00	t	2026-05-28	VCH-2026-05-022	22	0.00
143	5	2026	68000.00	30	22000.00	0.00	t	2026-05-28	VCH-2026-05-023	23	0.00
144	5	2026	68000.00	30	22000.00	0.00	t	2026-05-28	VCH-2026-05-024	24	0.00
145	5	2026	52000.00	30	17000.00	0.00	t	2026-05-28	VCH-2026-05-025	25	0.00
146	5	2026	52000.00	30	17000.00	0.00	t	2026-05-28	VCH-2026-05-026	26	0.00
147	5	2026	52000.00	30	17000.00	0.00	t	2026-05-28	VCH-2026-05-027	27	0.00
148	5	2026	38000.00	30	13000.00	0.00	t	2026-05-28	VCH-2026-05-028	28	0.00
149	5	2026	38000.00	30	13000.00	0.00	t	2026-05-28	VCH-2026-05-029	29	0.00
150	5	2026	38000.00	30	13000.00	0.00	t	2026-05-28	VCH-2026-05-030	30	0.00
151	6	2026	68000.00	30	22000.00	0.00	t	2026-06-28	VCH-2026-06-001	1	0.00
170	6	2026	68000.00	30	22000.00	0.00	t	2026-06-28	VCH-2026-06-020	20	0.00
171	6	2026	68000.00	30	22000.00	0.00	t	2026-06-28	VCH-2026-06-021	21	0.00
172	6	2026	68000.00	30	22000.00	0.00	t	2026-06-28	VCH-2026-06-022	22	0.00
173	6	2026	68000.00	30	22000.00	0.00	t	2026-06-28	VCH-2026-06-023	23	0.00
174	6	2026	68000.00	30	22000.00	0.00	t	2026-06-28	VCH-2026-06-024	24	0.00
175	6	2026	52000.00	30	17000.00	0.00	t	2026-06-28	VCH-2026-06-025	25	0.00
176	6	2026	52000.00	30	17000.00	0.00	t	2026-06-28	VCH-2026-06-026	26	0.00
177	6	2026	52000.00	30	17000.00	0.00	t	2026-06-28	VCH-2026-06-027	27	0.00
178	6	2026	38000.00	30	13000.00	0.00	t	2026-06-28	VCH-2026-06-028	28	0.00
179	6	2026	38000.00	30	13000.00	0.00	t	2026-06-28	VCH-2026-06-029	29	0.00
180	6	2026	38000.00	30	13000.00	0.00	t	2026-06-28	VCH-2026-06-030	30	0.00
181	7	2026	68000.00	30	22000.00	0.00	t	2026-07-28	VCH-2026-07-001	1	0.00
182	7	2026	68000.00	30	22000.00	0.00	t	2026-07-28	VCH-2026-07-002	2	0.00
183	7	2026	68000.00	30	22000.00	0.00	t	2026-07-28	VCH-2026-07-003	3	0.00
184	7	2026	68000.00	30	22000.00	0.00	t	2026-07-28	VCH-2026-07-004	4	0.00
185	7	2026	68000.00	30	22000.00	0.00	t	2026-07-28	VCH-2026-07-005	5	0.00
166	6	2026	38000.00	30	13000.00	0.00	t	2026-06-28	VCH-2026-06-016	16	0.00
186	7	2026	68000.00	30	22000.00	0.00	t	2026-07-28	VCH-2026-07-006	6	0.00
187	7	2026	52000.00	30	17000.00	0.00	t	2026-07-28	VCH-2026-07-007	7	0.00
188	7	2026	52000.00	30	17000.00	0.00	t	2026-07-28	VCH-2026-07-008	8	0.00
189	7	2026	52000.00	30	17000.00	0.00	t	2026-07-28	VCH-2026-07-009	9	0.00
190	7	2026	38000.00	30	13000.00	0.00	t	2026-07-28	VCH-2026-07-010	10	0.00
191	7	2026	38000.00	30	13000.00	0.00	t	2026-07-28	VCH-2026-07-011	11	0.00
192	7	2026	38000.00	30	13000.00	0.00	t	2026-07-28	VCH-2026-07-012	12	0.00
193	7	2026	28000.00	30	9000.00	0.00	t	2026-07-28	VCH-2026-07-013	13	0.00
194	7	2026	28000.00	30	9000.00	0.00	t	2026-07-28	VCH-2026-07-014	14	0.00
195	7	2026	38000.00	30	13000.00	0.00	t	2026-07-28	VCH-2026-07-015	15	0.00
196	7	2026	38000.00	30	13000.00	0.00	t	2026-07-28	VCH-2026-07-016	16	0.00
197	7	2026	45000.00	30	13000.00	0.00	t	2026-07-28	VCH-2026-07-017	17	0.00
198	7	2026	45000.00	30	13000.00	0.00	t	2026-07-28	VCH-2026-07-018	18	0.00
199	7	2026	68000.00	30	22000.00	0.00	t	2026-07-28	VCH-2026-07-019	19	0.00
200	7	2026	68000.00	30	22000.00	0.00	t	2026-07-28	VCH-2026-07-020	20	0.00
201	7	2026	68000.00	30	22000.00	0.00	t	2026-07-28	VCH-2026-07-021	21	0.00
202	7	2026	68000.00	30	22000.00	0.00	t	2026-07-28	VCH-2026-07-022	22	0.00
203	7	2026	68000.00	30	22000.00	0.00	t	2026-07-28	VCH-2026-07-023	23	0.00
204	7	2026	68000.00	30	22000.00	0.00	t	2026-07-28	VCH-2026-07-024	24	0.00
205	7	2026	52000.00	30	17000.00	0.00	t	2026-07-28	VCH-2026-07-025	25	0.00
206	7	2026	52000.00	30	17000.00	0.00	t	2026-07-28	VCH-2026-07-026	26	0.00
207	7	2026	52000.00	30	17000.00	0.00	t	2026-07-28	VCH-2026-07-027	27	0.00
208	7	2026	38000.00	30	13000.00	0.00	t	2026-07-28	VCH-2026-07-028	28	0.00
209	7	2026	38000.00	30	13000.00	0.00	t	2026-07-28	VCH-2026-07-029	29	0.00
210	7	2026	38000.00	30	13000.00	0.00	t	2026-07-28	VCH-2026-07-030	30	0.00
211	8	2026	68000.00	30	22000.00	0.00	f	\N	VCH-2026-08-001	1	0.00
212	8	2026	68000.00	30	22000.00	0.00	f	\N	VCH-2026-08-002	2	0.00
213	8	2026	68000.00	30	22000.00	0.00	f	\N	VCH-2026-08-003	3	0.00
214	8	2026	68000.00	30	22000.00	0.00	f	\N	VCH-2026-08-004	4	0.00
313	8	2026	28000.00	30	9000.00	0.00	f	\N		31	0.00
314	8	2026	28000.00	30	9000.00	0.00	f	\N		32	0.00
315	8	2026	38000.00	30	13000.00	0.00	f	\N		33	0.00
316	8	2026	38000.00	30	13000.00	0.00	f	\N		34	0.00
317	8	2026	45000.00	30	13000.00	0.00	f	\N		35	0.00
318	8	2026	45000.00	30	13000.00	0.00	f	\N		36	0.00
319	8	2026	68000.00	30	22000.00	0.00	f	\N		37	0.00
320	8	2026	68000.00	30	22000.00	0.00	f	\N		38	0.00
321	8	2026	68000.00	30	22000.00	0.00	f	\N		39	0.00
322	8	2026	68000.00	30	22000.00	0.00	f	\N		40	0.00
323	8	2026	68000.00	30	22000.00	0.00	f	\N		41	0.00
324	8	2026	68000.00	30	22000.00	0.00	f	\N		42	0.00
325	8	2026	52000.00	30	17000.00	0.00	f	\N		43	0.00
326	8	2026	52000.00	30	17000.00	0.00	f	\N		44	0.00
327	8	2026	52000.00	30	17000.00	0.00	f	\N		45	0.00
328	8	2026	38000.00	30	13000.00	0.00	f	\N		46	0.00
329	8	2026	38000.00	30	13000.00	0.00	f	\N		47	0.00
330	8	2026	38000.00	30	13000.00	0.00	f	\N		48	0.00
331	8	2026	28000.00	30	9000.00	0.00	f	\N		49	0.00
332	8	2026	28000.00	30	9000.00	0.00	f	\N		50	0.00
152	6	2026	68000.00	30	22000.00	0.00	t	2026-06-28	VCH-2026-06-002	2	0.00
153	6	2026	68000.00	30	22000.00	0.00	t	2026-06-28	VCH-2026-06-003	3	0.00
154	6	2026	68000.00	30	22000.00	0.00	t	2026-06-28	VCH-2026-06-004	4	0.00
155	6	2026	68000.00	30	22000.00	0.00	t	2026-06-28	VCH-2026-06-005	5	0.00
156	6	2026	68000.00	30	22000.00	0.00	t	2026-06-28	VCH-2026-06-006	6	0.00
157	6	2026	52000.00	30	17000.00	0.00	t	2026-06-28	VCH-2026-06-007	7	0.00
158	6	2026	52000.00	30	17000.00	0.00	t	2026-06-28	VCH-2026-06-008	8	0.00
159	6	2026	52000.00	30	17000.00	0.00	t	2026-06-28	VCH-2026-06-009	9	0.00
160	6	2026	38000.00	30	13000.00	0.00	t	2026-06-28	VCH-2026-06-010	10	0.00
161	6	2026	38000.00	30	13000.00	0.00	t	2026-06-28	VCH-2026-06-011	11	0.00
162	6	2026	38000.00	30	13000.00	0.00	t	2026-06-28	VCH-2026-06-012	12	0.00
163	6	2026	28000.00	30	9000.00	0.00	t	2026-06-28	VCH-2026-06-013	13	0.00
164	6	2026	28000.00	30	9000.00	0.00	t	2026-06-28	VCH-2026-06-014	14	0.00
165	6	2026	38000.00	30	13000.00	0.00	t	2026-06-28	VCH-2026-06-015	15	0.00
167	6	2026	45000.00	30	13000.00	0.00	t	2026-06-28	VCH-2026-06-017	17	0.00
168	6	2026	45000.00	30	13000.00	0.00	t	2026-06-28	VCH-2026-06-018	18	0.00
169	6	2026	68000.00	30	22000.00	0.00	t	2026-06-28	VCH-2026-06-019	19	0.00
215	8	2026	68000.00	30	22000.00	0.00	f	\N	VCH-2026-08-005	5	0.00
216	8	2026	68000.00	30	22000.00	0.00	f	\N	VCH-2026-08-006	6	0.00
217	8	2026	52000.00	30	17000.00	0.00	f	\N	VCH-2026-08-007	7	0.00
218	8	2026	52000.00	30	17000.00	0.00	f	\N	VCH-2026-08-008	8	0.00
219	8	2026	52000.00	30	17000.00	0.00	f	\N	VCH-2026-08-009	9	0.00
220	8	2026	38000.00	30	13000.00	0.00	f	\N	VCH-2026-08-010	10	0.00
221	8	2026	38000.00	30	13000.00	0.00	f	\N	VCH-2026-08-011	11	0.00
222	8	2026	38000.00	30	13000.00	0.00	f	\N	VCH-2026-08-012	12	0.00
223	8	2026	28000.00	30	9000.00	0.00	f	\N	VCH-2026-08-013	13	0.00
224	8	2026	28000.00	30	9000.00	0.00	f	\N	VCH-2026-08-014	14	0.00
225	8	2026	38000.00	30	13000.00	0.00	f	\N	VCH-2026-08-015	15	0.00
226	8	2026	38000.00	30	13000.00	0.00	f	\N	VCH-2026-08-016	16	0.00
227	8	2026	45000.00	30	13000.00	0.00	f	\N	VCH-2026-08-017	17	0.00
228	8	2026	45000.00	30	13000.00	0.00	f	\N	VCH-2026-08-018	18	0.00
229	8	2026	68000.00	30	22000.00	0.00	f	\N	VCH-2026-08-019	19	0.00
230	8	2026	68000.00	30	22000.00	0.00	f	\N	VCH-2026-08-020	20	0.00
231	8	2026	68000.00	30	22000.00	0.00	f	\N	VCH-2026-08-021	21	0.00
232	8	2026	68000.00	30	22000.00	0.00	f	\N	VCH-2026-08-022	22	0.00
233	8	2026	68000.00	30	22000.00	0.00	f	\N	VCH-2026-08-023	23	0.00
234	8	2026	68000.00	30	22000.00	0.00	f	\N	VCH-2026-08-024	24	0.00
235	8	2026	52000.00	30	17000.00	0.00	f	\N	VCH-2026-08-025	25	0.00
236	8	2026	52000.00	30	17000.00	0.00	f	\N	VCH-2026-08-026	26	0.00
237	8	2026	52000.00	30	17000.00	0.00	f	\N	VCH-2026-08-027	27	0.00
238	8	2026	38000.00	30	13000.00	0.00	f	\N	VCH-2026-08-028	28	0.00
239	8	2026	38000.00	30	13000.00	0.00	f	\N	VCH-2026-08-029	29	0.00
240	8	2026	38000.00	30	13000.00	0.00	f	\N	VCH-2026-08-030	30	0.00
\.


--
-- Data for Name: teachers_salaryscale; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.teachers_salaryscale (id, name, basic_pay, medical_allowance, conveyance_allowance, other_allowances) FROM stdin;
6	BPS-16	25000.00	2000.00	3000.00	0.00
1	PST Scale (Grade 12)	28000.00	3000.00	4000.00	2000.00
2	CT Scale (Grade 15)	38000.00	4500.00	5500.00	3000.00
3	SST Science (Grade 16)	52000.00	6000.00	7000.00	4000.00
4	Lecturer F.Sc (Grade 17)	68000.00	8000.00	9000.00	5000.00
5	Admin & Accounts Scale	45000.00	5000.00	5000.00	3000.00
\.


--
-- Data for Name: teachers_teacher; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.teachers_teacher (id, teacher_id, full_name, father_name, cnic, dob, qualification, experience, contact_number, address, joining_date, designation, profile_picture, status, remarks, salary_scale_id) FROM stdin;
27	T-027	Shahzad Ali	Moiz Jan	15602-2782253-1	1992-08-19	M.Phil / Master Degree in relevant subject	12 years teaching experience	03455356373	Mingora City, Swat KPK	2018-08-12	Urdu & Pashto Teacher		Active		3
28	T-028	Danish Swati	Salman Yousafzai	15602-7282016-1	1982-06-02	M.Phil / Master Degree in relevant subject	3 years teaching experience	03472875566	Qalagay, Tehsil Barikot, District Swat	2018-10-15	Islamic Studies Teacher		Active		2
29	T-029	Gulzar Hussain	Ibrahim Zada	15602-9706496-1	1994-07-16	M.Phil / Master Degree in relevant subject	14 years teaching experience	03129029282	Kabal Main Road, Swat	2019-06-24	Pakistan Studies Teacher		Active		2
30	T-030	Sana Bibi	Umar Hussain	15602-1889035-1	1978-09-14	M.Phil / Master Degree in relevant subject	3 years teaching experience	03459670158	Mingora City, Swat KPK	2021-08-07	General Science Teacher		Active		2
39	T-039	Hazrat Zada	Umar Gul	15602-5917747-1	1980-09-24	M.Phil / Master Degree in relevant subject	8 years teaching experience	03457776176	Mingora City, Swat KPK	2018-08-15	Senior English Lecturer		Active		4
41	T-041	Haris Khan	Saad Khan	15602-8318357-1	1995-10-09	M.Phil / Master Degree in relevant subject	14 years teaching experience	03339233048	Main Bazaar Qalagay, Swat	2022-04-19	Chemistry Lecturer		Active		4
42	T-042	Bilal Shah	Junaid Ahmad	15602-8073480-1	1993-12-13	M.Phil / Master Degree in relevant subject	3 years teaching experience	03457344253	Barikot Central, Swat KPK	2021-08-03	Biology Lecturer		Active		4
59	T-999	Rashid Zada			1995-05-10	BS Computer Science	5 Years	0347-0983567		2026-09-05	IT Incharge / Full Stack Developer		Active		4
23	T-023	Hamza Gul	Shoaib Ali	15602-5647256-1	1987-05-04	M.Phil / Master Degree in relevant subject	5 years teaching experience	03127797452	Qalagay, Tehsil Barikot, District Swat	2023-12-08	Chemistry Lecturer		Active		4
24	T-024	Mustafa Hussain	Waleed Jan	15602-3610447-1	1993-02-27	M.Phil / Master Degree in relevant subject	9 years teaching experience	03479164551	Kabal Main Road, Swat	2023-03-24	Biology Lecturer		Active		4
25	T-025	Sidra Bibi	Shahzad Ahmad	15602-6844288-1	1988-04-05	M.Phil / Master Degree in relevant subject	10 years teaching experience	03315280624	Main Bazaar Qalagay, Swat	2020-08-28	Mathematics Specialist		Active		3
26	T-026	Salman Zada	Ibrahim Jan	15602-8188622-1	1980-03-24	M.Phil / Master Degree in relevant subject	13 years teaching experience	03477612487	Kabal Main Road, Swat	2018-04-19	Computer Science Instructor		Active		3
43	T-043	Abdullah Bibi	Sameer Khan	15602-8969499-1	1985-02-19	M.Phil / Master Degree in relevant subject	3 years teaching experience	03331101162	Barikot Central, Swat KPK	2021-12-08	Mathematics Specialist		Active		3
44	T-044	Tariq Jan	Ali Swati	15602-9526029-1	1987-08-12	M.Phil / Master Degree in relevant subject	15 years teaching experience	03451172354	Mingora City, Swat KPK	2021-05-03	Computer Science Instructor		Active		3
45	T-045	Sadia Gul	Salman Ahmad	15602-4643355-1	1985-04-06	M.Phil / Master Degree in relevant subject	15 years teaching experience	03332461557	Saidu Sharif Near Central Hospital, Swat	2023-01-04	Urdu & Pashto Teacher		Active		3
49	T-049	Rizwan Jan	Fazal Khan	15602-5905954-1	1987-12-15	M.Phil / Master Degree in relevant subject	5 years teaching experience	03006780383	Main Bazaar Qalagay, Swat	2021-10-16	Primary Class Teacher		Active		1
1	T-001	Dr. Farman Ali	Tariq Gul	15602-4835727-1	1982-11-02	M.Phil / Master Degree in relevant subject	9 years teaching experience	+92 344 9631323	Matta Road, Swat KPK	2019-05-25	Principal		Active		4
2	T-002	Umar Saeed	Kashan Gul	15602-2804339-1	1990-07-22	M.Phil / Master Degree in relevant subject	8 years teaching experience	+92 345 3407095	Matta Road, Swat KPK	2023-10-04	Vice Principal		Active		4
56	10001	Gul Zeb	M Zeb	156040933554	1995-09-22	Msc English	Five Years	03419540730	Totano bandai Qalagay Kabal swat Kpk Pakistan	2026-09-04	PST	teachers/ChatGPT_Image_Sep_4_2026_01_23_22_AM.png	Active		1
3	T-003	Hamza Rehman	Ibrahim Rehman	15602-1096477-1	1985-01-24	M.Phil / Master Degree in relevant subject	3 years teaching experience	03312987085	Qalagay, Tehsil Barikot, District Swat	2020-07-07	Senior English Lecturer		Active		4
4	T-004	Junaid Hussain	Shaukat Gul	15602-2936293-1	1986-10-04	M.Phil / Master Degree in relevant subject	6 years teaching experience	03123740761	Saidu Sharif Near Central Hospital, Swat	2021-01-22	Physics Lecturer		Active		4
5	T-005	Ayesha Khan	Danish Swati	15602-9422907-1	1980-01-08	M.Phil / Master Degree in relevant subject	7 years teaching experience	03334999448	Mingora City, Swat KPK	2024-01-28	Chemistry Lecturer		Active		4
6	T-006	Ali Hussain	Talha Khan	15602-4318865-1	1995-03-22	M.Phil / Master Degree in relevant subject	3 years teaching experience	03457464551	Ghalegay Near Rock Carving, Swat	2018-06-23	Biology Lecturer		Active		4
7	T-007	Adil Zada	Bakht Zada	15602-7469282-1	1994-11-26	M.Phil / Master Degree in relevant subject	14 years teaching experience	03338423255	Barikot Central, Swat KPK	2022-09-20	Mathematics Specialist		Active		3
8	T-008	Zeeshan Rehman	Salman Rehman	15602-3202279-1	1979-07-24	M.Phil / Master Degree in relevant subject	9 years teaching experience	03477889259	Ghalegay Near Rock Carving, Swat	2021-05-22	Computer Science Instructor		Active		3
9	T-009	Zain Zada	Salman Swati	15602-1898017-1	1987-11-20	M.Phil / Master Degree in relevant subject	8 years teaching experience	03002843211	Saidu Sharif Near Central Hospital, Swat	2022-07-17	Urdu & Pashto Teacher		Active		3
10	T-010	Hira Khan	Mustafa Jan	15602-2192414-1	1980-12-23	M.Phil / Master Degree in relevant subject	6 years teaching experience	03124091105	Mingora City, Swat KPK	2023-12-05	Islamic Studies Teacher		Active		2
40	T-040	Hira Gul	Usman Yousafzai	15602-2152091-1	1983-07-12	M.Phil / Master Degree in relevant subject	3 years teaching experience	03334411559	Mingora City, Swat KPK	2023-12-16	Physics Lecturer		Active		4
46	T-046	Adil Ali	Fazal Gul	15602-1371077-1	1978-01-10	M.Phil / Master Degree in relevant subject	7 years teaching experience	03313486853	Kabal Main Road, Swat	2023-02-28	Islamic Studies Teacher		Active		2
47	T-047	Zain Shah	Danish Ali	15602-6530119-1	1982-01-17	M.Phil / Master Degree in relevant subject	15 years teaching experience	03129272858	Saidu Sharif Near Central Hospital, Swat	2023-05-12	Pakistan Studies Teacher		Active		2
48	T-048	Noman Ali	Fazal Gul	15602-6976648-1	1983-08-03	M.Phil / Master Degree in relevant subject	6 years teaching experience	03123259340	Barikot Central, Swat KPK	2021-01-03	General Science Teacher		Active		2
50	T-050	Ayesha Khan	Aman Ahmad	15602-5297881-1	1992-06-23	M.Phil / Master Degree in relevant subject	14 years teaching experience	03123532081	Saidu Sharif Near Central Hospital, Swat	2020-10-23	Early Childhood Trainer		Active		1
51	T-051	Zain Hussain	Ahmad Rehman	15602-7788745-1	1978-04-15	M.Phil / Master Degree in relevant subject	14 years teaching experience	03453304846	Main Bazaar Qalagay, Swat	2023-03-13	Physical Training Instructor (PTI)		Inactive		2
52	T-052	Waleed Shah	Gulzar Ali	15602-1729737-1	1991-05-19	M.Phil / Master Degree in relevant subject	15 years teaching experience	03456928273	Matta Road, Swat KPK	2021-06-23	Senior Librarian		Inactive		2
53	T-053	Noman Zada	Haris Rehman	15602-7101682-1	1976-03-24	M.Phil / Master Degree in relevant subject	13 years teaching experience	03457129569	Main Bazaar Qalagay, Swat	2022-03-01	Chief Accountant		Inactive		5
54	T-054	Tariq Hussain	Junaid Yousafzai	15602-9866614-1	1992-06-04	M.Phil / Master Degree in relevant subject	7 years teaching experience	03458474544	Khwazakhela Bazaar, Swat	2021-05-18	Office Superintendent		Inactive		5
55	T-055	Mehwish Gul	Salman Swati	15602-2908448-1	1978-11-04	M.Phil / Master Degree in relevant subject	9 years teaching experience	03001950831	Ghalegay Near Rock Carving, Swat	2021-05-11	Principal		Inactive		4
11	T-011	Ahmad Shah	Hamza Zada	15602-8342486-1	1981-08-21	M.Phil / Master Degree in relevant subject	8 years teaching experience	03474142478	Saidu Sharif Near Central Hospital, Swat	2024-09-18	Pakistan Studies Teacher		Active		2
12	T-012	Muhammad Hussain	Umar Gul	15602-7616130-1	1987-09-06	M.Phil / Master Degree in relevant subject	12 years teaching experience	03006757603	Ghalegay Near Rock Carving, Swat	2022-04-18	General Science Teacher		Active		2
13	T-013	Zain Zada	Hamza Zada	15602-6994218-1	1980-03-16	M.Phil / Master Degree in relevant subject	7 years teaching experience	03473776405	Khwazakhela Bazaar, Swat	2020-11-12	Primary Class Teacher		Active		1
14	T-014	Zain Bibi	Gulzar Hussain	15602-1490277-1	1993-07-28	M.Phil / Master Degree in relevant subject	11 years teaching experience	03334109171	Saidu Sharif Near Central Hospital, Swat	2022-12-09	Early Childhood Trainer		Active		1
15	T-015	Hafsa Bibi	Bakht Jan	15602-7676003-1	1982-02-22	M.Phil / Master Degree in relevant subject	10 years teaching experience	03008764254	Main Bazaar Qalagay, Swat	2018-06-23	Physical Training Instructor (PTI)		Active		2
16	T-016	Moiz Gul	Zain Hussain	15602-8784441-1	1995-10-10	M.Phil / Master Degree in relevant subject	15 years teaching experience	03006804883	Ghalegay Near Rock Carving, Swat	2018-09-04	Senior Librarian		Active		2
17	T-017	Taimur Yousafzai	Abdullah Swati	15602-3684388-1	1993-01-11	M.Phil / Master Degree in relevant subject	14 years teaching experience	03473957251	Qalagay, Tehsil Barikot, District Swat	2021-06-16	Chief Accountant		Active		5
18	T-018	Noman Ali	Ali Ali	15602-8173048-1	1987-02-07	M.Phil / Master Degree in relevant subject	3 years teaching experience	03317688786	Mingora City, Swat KPK	2023-03-10	Office Superintendent		Active		5
19	T-019	Kashan Yousafzai	Zain Shah	15602-2565259-1	1988-05-26	M.Phil / Master Degree in relevant subject	7 years teaching experience	03334584240	Saidu Sharif Near Central Hospital, Swat	2018-01-06	Principal		Active		4
20	T-020	Iqra Khan	Zubair Hussain	15602-9767430-1	1980-02-15	M.Phil / Master Degree in relevant subject	14 years teaching experience	03472445281	Kabal Main Road, Swat	2019-02-10	Vice Principal		Active		4
21	T-021	Shaukat Zada	Fazal Rehman	15602-1839205-1	1982-12-19	M.Phil / Master Degree in relevant subject	8 years teaching experience	03311586361	Mingora City, Swat KPK	2022-03-14	Senior English Lecturer		Active		4
22	T-022	Shoaib Rehman	Taimur Gul	15602-1472968-1	1986-08-17	M.Phil / Master Degree in relevant subject	9 years teaching experience	03339327918	Matta Road, Swat KPK	2023-01-01	Physics Lecturer		Active		4
31	T-031	Waleed Zada	Saad Gul	15602-4690548-1	1975-01-23	M.Phil / Master Degree in relevant subject	11 years teaching experience	03121968658	Saidu Sharif Near Central Hospital, Swat	2023-04-17	Primary Class Teacher		Active		1
32	T-032	Ahmad Yousafzai	Shaukat Bibi	15602-1108150-1	1984-05-01	M.Phil / Master Degree in relevant subject	15 years teaching experience	03456281054	Mingora City, Swat KPK	2024-06-07	Early Childhood Trainer		Active		1
33	T-033	Shaukat Swati	Ali Shah	15602-2557364-1	1994-08-09	M.Phil / Master Degree in relevant subject	6 years teaching experience	03314035589	Main Bazaar Qalagay, Swat	2022-12-06	Physical Training Instructor (PTI)		Active		2
34	T-034	Gulzar Bibi	Hazrat Shah	15602-3014824-1	1982-11-18	M.Phil / Master Degree in relevant subject	14 years teaching experience	03472277940	Mingora City, Swat KPK	2022-01-01	Senior Librarian		Active		2
35	T-035	Zainab Gul	Sameer Jan	15602-5365030-1	1984-05-09	M.Phil / Master Degree in relevant subject	6 years teaching experience	03127705612	Matta Road, Swat KPK	2018-09-24	Chief Accountant		Active		5
36	T-036	Abdullah Ahmad	Junaid Ahmad	15602-6006711-1	1994-09-06	M.Phil / Master Degree in relevant subject	6 years teaching experience	03001768954	Matta Road, Swat KPK	2023-06-22	Office Superintendent		Active		5
37	T-037	Sami Zada	Muhammad Ahmad	15602-4230872-1	1978-07-13	M.Phil / Master Degree in relevant subject	15 years teaching experience	03006615721	Qalagay, Tehsil Barikot, District Swat	2023-05-24	Principal		Active		4
38	T-038	Sameer Shah	Sami Swati	15602-7393013-1	1990-06-23	M.Phil / Master Degree in relevant subject	11 years teaching experience	03458677896	Mingora City, Swat KPK	2021-12-25	Vice Principal		Active		4
\.


--
-- Name: accounts_expense_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.accounts_expense_id_seq', 33, true);


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 96, true);


--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_user_groups_id_seq', 1, false);


--
-- Name: auth_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_user_id_seq', 2, true);


--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_user_user_permissions_id_seq', 1, false);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 3, true);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 24, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 27, true);


--
-- Name: exams_classsubject_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exams_classsubject_id_seq', 148, true);


--
-- Name: exams_exam_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exams_exam_id_seq', 3, true);


--
-- Name: exams_exammark_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exams_exammark_id_seq', 160, true);


--
-- Name: exams_subject_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exams_subject_id_seq', 16, true);


--
-- Name: finance_feepaymentreceipt_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.finance_feepaymentreceipt_id_seq', 60, true);


--
-- Name: finance_feepaymentreceipt_month_entries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.finance_feepaymentreceipt_month_entries_id_seq', 106, true);


--
-- Name: finance_studentfeeledger_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.finance_studentfeeledger_id_seq', 161, true);


--
-- Name: finance_studentfeemonthentry_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.finance_studentfeemonthentry_id_seq', 1932, true);


--
-- Name: school_academicsession_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.school_academicsession_id_seq', 3, true);


--
-- Name: school_classlevel_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.school_classlevel_id_seq', 18, true);


--
-- Name: school_schoolsetting_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.school_schoolsetting_id_seq', 1, true);


--
-- Name: school_section_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.school_section_id_seq', 36, true);


--
-- Name: students_familyhousehold_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.students_familyhousehold_id_seq', 48, true);


--
-- Name: students_promotionhistory_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.students_promotionhistory_id_seq', 8, true);


--
-- Name: students_student_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.students_student_id_seq', 163, true);


--
-- Name: teachers_monthlysalarybill_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.teachers_monthlysalarybill_id_seq', 333, true);


--
-- Name: teachers_salaryscale_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.teachers_salaryscale_id_seq', 6, true);


--
-- Name: teachers_teacher_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.teachers_teacher_id_seq', 59, true);


--
-- Name: accounts_expense accounts_expense_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accounts_expense
    ADD CONSTRAINT accounts_expense_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission auth_permission_content_type_id_codename_01ab375a_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- Name: auth_permission auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups auth_user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups auth_user_groups_user_id_group_id_94350c0c_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_group_id_94350c0c_uniq UNIQUE (user_id, group_id);


--
-- Name: auth_user auth_user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_user
    ADD CONSTRAINT auth_user_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions auth_user_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions auth_user_user_permissions_user_id_permission_id_14a6b632_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_permission_id_14a6b632_uniq UNIQUE (user_id, permission_id);


--
-- Name: auth_user auth_user_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_user
    ADD CONSTRAINT auth_user_username_key UNIQUE (username);


--
-- Name: django_admin_log django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type django_content_type_app_label_model_76bd3d3b_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_session django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: exams_classsubject exams_classsubject_class_level_id_subject_id_78b4658b_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exams_classsubject
    ADD CONSTRAINT exams_classsubject_class_level_id_subject_id_78b4658b_uniq UNIQUE (class_level_id, subject_id);


--
-- Name: exams_classsubject exams_classsubject_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exams_classsubject
    ADD CONSTRAINT exams_classsubject_pkey PRIMARY KEY (id);


--
-- Name: exams_exam exams_exam_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exams_exam
    ADD CONSTRAINT exams_exam_pkey PRIMARY KEY (id);


--
-- Name: exams_exammark exams_exammark_exam_id_student_id_subject_id_9db8e81e_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exams_exammark
    ADD CONSTRAINT exams_exammark_exam_id_student_id_subject_id_9db8e81e_uniq UNIQUE (exam_id, student_id, subject_id);


--
-- Name: exams_exammark exams_exammark_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exams_exammark
    ADD CONSTRAINT exams_exammark_pkey PRIMARY KEY (id);


--
-- Name: exams_subject exams_subject_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exams_subject
    ADD CONSTRAINT exams_subject_name_key UNIQUE (name);


--
-- Name: exams_subject exams_subject_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exams_subject
    ADD CONSTRAINT exams_subject_pkey PRIMARY KEY (id);


--
-- Name: finance_feepaymentreceipt_month_entries finance_feepaymentreceip_feepaymentreceipt_id_stu_5fa12f1a_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_feepaymentreceipt_month_entries
    ADD CONSTRAINT finance_feepaymentreceip_feepaymentreceipt_id_stu_5fa12f1a_uniq UNIQUE (feepaymentreceipt_id, studentfeemonthentry_id);


--
-- Name: finance_feepaymentreceipt_month_entries finance_feepaymentreceipt_month_entries_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_feepaymentreceipt_month_entries
    ADD CONSTRAINT finance_feepaymentreceipt_month_entries_pkey PRIMARY KEY (id);


--
-- Name: finance_feepaymentreceipt finance_feepaymentreceipt_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_feepaymentreceipt
    ADD CONSTRAINT finance_feepaymentreceipt_pkey PRIMARY KEY (id);


--
-- Name: finance_feepaymentreceipt finance_feepaymentreceipt_receipt_no_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_feepaymentreceipt
    ADD CONSTRAINT finance_feepaymentreceipt_receipt_no_key UNIQUE (receipt_no);


--
-- Name: finance_studentfeeledger finance_studentfeeledger_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_studentfeeledger
    ADD CONSTRAINT finance_studentfeeledger_pkey PRIMARY KEY (id);


--
-- Name: finance_studentfeeledger finance_studentfeeledger_student_id_academic_sess_851f7590_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_studentfeeledger
    ADD CONSTRAINT finance_studentfeeledger_student_id_academic_sess_851f7590_uniq UNIQUE (student_id, academic_session_id);


--
-- Name: finance_studentfeemonthentry finance_studentfeemonthentry_ledger_id_month_9462bee3_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_studentfeemonthentry
    ADD CONSTRAINT finance_studentfeemonthentry_ledger_id_month_9462bee3_uniq UNIQUE (ledger_id, month);


--
-- Name: finance_studentfeemonthentry finance_studentfeemonthentry_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_studentfeemonthentry
    ADD CONSTRAINT finance_studentfeemonthentry_pkey PRIMARY KEY (id);


--
-- Name: school_academicsession school_academicsession_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.school_academicsession
    ADD CONSTRAINT school_academicsession_name_key UNIQUE (name);


--
-- Name: school_academicsession school_academicsession_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.school_academicsession
    ADD CONSTRAINT school_academicsession_pkey PRIMARY KEY (id);


--
-- Name: school_classlevel school_classlevel_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.school_classlevel
    ADD CONSTRAINT school_classlevel_name_key UNIQUE (name);


--
-- Name: school_classlevel school_classlevel_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.school_classlevel
    ADD CONSTRAINT school_classlevel_pkey PRIMARY KEY (id);


--
-- Name: school_schoolsetting school_schoolsetting_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.school_schoolsetting
    ADD CONSTRAINT school_schoolsetting_pkey PRIMARY KEY (id);


--
-- Name: school_section school_section_class_level_id_name_bdec3baa_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.school_section
    ADD CONSTRAINT school_section_class_level_id_name_bdec3baa_uniq UNIQUE (class_level_id, name);


--
-- Name: school_section school_section_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.school_section
    ADD CONSTRAINT school_section_pkey PRIMARY KEY (id);


--
-- Name: students_familyhousehold students_familyhousehold_family_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_familyhousehold
    ADD CONSTRAINT students_familyhousehold_family_id_key UNIQUE (family_id);


--
-- Name: students_familyhousehold students_familyhousehold_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_familyhousehold
    ADD CONSTRAINT students_familyhousehold_pkey PRIMARY KEY (id);


--
-- Name: students_promotionhistory students_promotionhistory_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_promotionhistory
    ADD CONSTRAINT students_promotionhistory_pkey PRIMARY KEY (id);


--
-- Name: students_student students_student_admission_no_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_student
    ADD CONSTRAINT students_student_admission_no_key UNIQUE (admission_no);


--
-- Name: students_student students_student_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_student
    ADD CONSTRAINT students_student_pkey PRIMARY KEY (id);


--
-- Name: teachers_monthlysalarybill teachers_monthlysalarybill_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teachers_monthlysalarybill
    ADD CONSTRAINT teachers_monthlysalarybill_pkey PRIMARY KEY (id);


--
-- Name: teachers_monthlysalarybill teachers_monthlysalarybill_teacher_id_month_year_6e9825e4_uniq; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teachers_monthlysalarybill
    ADD CONSTRAINT teachers_monthlysalarybill_teacher_id_month_year_6e9825e4_uniq UNIQUE (teacher_id, month, year);


--
-- Name: teachers_salaryscale teachers_salaryscale_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teachers_salaryscale
    ADD CONSTRAINT teachers_salaryscale_name_key UNIQUE (name);


--
-- Name: teachers_salaryscale teachers_salaryscale_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teachers_salaryscale
    ADD CONSTRAINT teachers_salaryscale_pkey PRIMARY KEY (id);


--
-- Name: teachers_teacher teachers_teacher_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teachers_teacher
    ADD CONSTRAINT teachers_teacher_pkey PRIMARY KEY (id);


--
-- Name: teachers_teacher teachers_teacher_teacher_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teachers_teacher
    ADD CONSTRAINT teachers_teacher_teacher_id_key UNIQUE (teacher_id);


--
-- Name: auth_group_name_a6ea08ec_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_group_name_a6ea08ec_like ON public.auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_group_id_b120cbf9; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON public.auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_permission_id_84c5c92e; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON public.auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_content_type_id_2f476e4b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_permission_content_type_id_2f476e4b ON public.auth_permission USING btree (content_type_id);


--
-- Name: auth_user_groups_group_id_97559544; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_user_groups_group_id_97559544 ON public.auth_user_groups USING btree (group_id);


--
-- Name: auth_user_groups_user_id_6a12ed8b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_user_groups_user_id_6a12ed8b ON public.auth_user_groups USING btree (user_id);


--
-- Name: auth_user_user_permissions_permission_id_1fbb5f2c; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_user_user_permissions_permission_id_1fbb5f2c ON public.auth_user_user_permissions USING btree (permission_id);


--
-- Name: auth_user_user_permissions_user_id_a95ead1b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_user_user_permissions_user_id_a95ead1b ON public.auth_user_user_permissions USING btree (user_id);


--
-- Name: auth_user_username_6821ab7c_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX auth_user_username_6821ab7c_like ON public.auth_user USING btree (username varchar_pattern_ops);


--
-- Name: django_admin_log_content_type_id_c4bce8eb; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON public.django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id_c564eba6; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_admin_log_user_id_c564eba6 ON public.django_admin_log USING btree (user_id);


--
-- Name: django_session_expire_date_a5c62663; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_session_expire_date_a5c62663 ON public.django_session USING btree (expire_date);


--
-- Name: django_session_session_key_c0390e0f_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX django_session_session_key_c0390e0f_like ON public.django_session USING btree (session_key varchar_pattern_ops);


--
-- Name: exams_classsubject_class_level_id_1cf805ba; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX exams_classsubject_class_level_id_1cf805ba ON public.exams_classsubject USING btree (class_level_id);


--
-- Name: exams_classsubject_subject_id_c4ba1111; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX exams_classsubject_subject_id_c4ba1111 ON public.exams_classsubject USING btree (subject_id);


--
-- Name: exams_exam_session_id_97602d19; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX exams_exam_session_id_97602d19 ON public.exams_exam USING btree (session_id);


--
-- Name: exams_exammark_class_level_id_9d13595d; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX exams_exammark_class_level_id_9d13595d ON public.exams_exammark USING btree (class_level_id);


--
-- Name: exams_exammark_exam_id_0e1ee69b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX exams_exammark_exam_id_0e1ee69b ON public.exams_exammark USING btree (exam_id);


--
-- Name: exams_exammark_student_id_fcc2fb05; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX exams_exammark_student_id_fcc2fb05 ON public.exams_exammark USING btree (student_id);


--
-- Name: exams_exammark_subject_id_b114cf98; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX exams_exammark_subject_id_b114cf98 ON public.exams_exammark USING btree (subject_id);


--
-- Name: exams_subject_name_ec73097d_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX exams_subject_name_ec73097d_like ON public.exams_subject USING btree (name varchar_pattern_ops);


--
-- Name: finance_feepaymentreceipt__feepaymentreceipt_id_8da561d4; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX finance_feepaymentreceipt__feepaymentreceipt_id_8da561d4 ON public.finance_feepaymentreceipt_month_entries USING btree (feepaymentreceipt_id);


--
-- Name: finance_feepaymentreceipt__studentfeemonthentry_id_88f8f2aa; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX finance_feepaymentreceipt__studentfeemonthentry_id_88f8f2aa ON public.finance_feepaymentreceipt_month_entries USING btree (studentfeemonthentry_id);


--
-- Name: finance_feepaymentreceipt_receipt_no_2a5aaf5c_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX finance_feepaymentreceipt_receipt_no_2a5aaf5c_like ON public.finance_feepaymentreceipt USING btree (receipt_no varchar_pattern_ops);


--
-- Name: finance_feepaymentreceipt_student_id_0286c392; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX finance_feepaymentreceipt_student_id_0286c392 ON public.finance_feepaymentreceipt USING btree (student_id);


--
-- Name: finance_studentfeeledger_academic_session_id_98fdaaac; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX finance_studentfeeledger_academic_session_id_98fdaaac ON public.finance_studentfeeledger USING btree (academic_session_id);


--
-- Name: finance_studentfeeledger_student_id_6819ba4c; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX finance_studentfeeledger_student_id_6819ba4c ON public.finance_studentfeeledger USING btree (student_id);


--
-- Name: finance_studentfeemonthentry_ledger_id_e4c9a9e7; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX finance_studentfeemonthentry_ledger_id_e4c9a9e7 ON public.finance_studentfeemonthentry USING btree (ledger_id);


--
-- Name: school_academicsession_name_f698a586_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX school_academicsession_name_f698a586_like ON public.school_academicsession USING btree (name varchar_pattern_ops);


--
-- Name: school_classlevel_name_45e68f6f_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX school_classlevel_name_45e68f6f_like ON public.school_classlevel USING btree (name varchar_pattern_ops);


--
-- Name: school_section_class_level_id_0c997e4a; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX school_section_class_level_id_0c997e4a ON public.school_section USING btree (class_level_id);


--
-- Name: students_familyhousehold_family_id_0db3cd5b_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX students_familyhousehold_family_id_0db3cd5b_like ON public.students_familyhousehold USING btree (family_id varchar_pattern_ops);


--
-- Name: students_promotionhistory_from_class_id_7189d79c; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX students_promotionhistory_from_class_id_7189d79c ON public.students_promotionhistory USING btree (from_class_id);


--
-- Name: students_promotionhistory_from_section_id_9305de88; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX students_promotionhistory_from_section_id_9305de88 ON public.students_promotionhistory USING btree (from_section_id);


--
-- Name: students_promotionhistory_student_id_66feb5eb; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX students_promotionhistory_student_id_66feb5eb ON public.students_promotionhistory USING btree (student_id);


--
-- Name: students_promotionhistory_to_class_id_d284316c; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX students_promotionhistory_to_class_id_d284316c ON public.students_promotionhistory USING btree (to_class_id);


--
-- Name: students_promotionhistory_to_section_id_ec1f7bb7; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX students_promotionhistory_to_section_id_ec1f7bb7 ON public.students_promotionhistory USING btree (to_section_id);


--
-- Name: students_student_admission_no_feb174a2_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX students_student_admission_no_feb174a2_like ON public.students_student USING btree (admission_no varchar_pattern_ops);


--
-- Name: students_student_current_class_id_cf5f558b; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX students_student_current_class_id_cf5f558b ON public.students_student USING btree (current_class_id);


--
-- Name: students_student_current_section_id_3239129f; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX students_student_current_section_id_3239129f ON public.students_student USING btree (current_section_id);


--
-- Name: students_student_family_id_bbc9cc99; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX students_student_family_id_bbc9cc99 ON public.students_student USING btree (family_id);


--
-- Name: teachers_monthlysalarybill_teacher_id_cc1084ca; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX teachers_monthlysalarybill_teacher_id_cc1084ca ON public.teachers_monthlysalarybill USING btree (teacher_id);


--
-- Name: teachers_salaryscale_name_829c87a9_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX teachers_salaryscale_name_829c87a9_like ON public.teachers_salaryscale USING btree (name varchar_pattern_ops);


--
-- Name: teachers_teacher_salary_scale_id_e526c2c8; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX teachers_teacher_salary_scale_id_e526c2c8 ON public.teachers_teacher USING btree (salary_scale_id);


--
-- Name: teachers_teacher_teacher_id_d2057e5f_like; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX teachers_teacher_teacher_id_d2057e5f_like ON public.teachers_teacher USING btree (teacher_id varchar_pattern_ops);


--
-- Name: auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups auth_user_groups_group_id_97559544_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_group_id_97559544_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups auth_user_groups_user_id_6a12ed8b_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_6a12ed8b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permissions auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permissions auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_user_id_c564eba6_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exams_classsubject exams_classsubject_class_level_id_1cf805ba_fk_school_cl; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exams_classsubject
    ADD CONSTRAINT exams_classsubject_class_level_id_1cf805ba_fk_school_cl FOREIGN KEY (class_level_id) REFERENCES public.school_classlevel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exams_classsubject exams_classsubject_subject_id_c4ba1111_fk_exams_subject_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exams_classsubject
    ADD CONSTRAINT exams_classsubject_subject_id_c4ba1111_fk_exams_subject_id FOREIGN KEY (subject_id) REFERENCES public.exams_subject(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exams_exam exams_exam_session_id_97602d19_fk_school_academicsession_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exams_exam
    ADD CONSTRAINT exams_exam_session_id_97602d19_fk_school_academicsession_id FOREIGN KEY (session_id) REFERENCES public.school_academicsession(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exams_exammark exams_exammark_class_level_id_9d13595d_fk_school_classlevel_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exams_exammark
    ADD CONSTRAINT exams_exammark_class_level_id_9d13595d_fk_school_classlevel_id FOREIGN KEY (class_level_id) REFERENCES public.school_classlevel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exams_exammark exams_exammark_exam_id_0e1ee69b_fk_exams_exam_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exams_exammark
    ADD CONSTRAINT exams_exammark_exam_id_0e1ee69b_fk_exams_exam_id FOREIGN KEY (exam_id) REFERENCES public.exams_exam(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exams_exammark exams_exammark_student_id_fcc2fb05_fk_students_student_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exams_exammark
    ADD CONSTRAINT exams_exammark_student_id_fcc2fb05_fk_students_student_id FOREIGN KEY (student_id) REFERENCES public.students_student(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exams_exammark exams_exammark_subject_id_b114cf98_fk_exams_subject_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exams_exammark
    ADD CONSTRAINT exams_exammark_subject_id_b114cf98_fk_exams_subject_id FOREIGN KEY (subject_id) REFERENCES public.exams_subject(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: finance_feepaymentreceipt_month_entries finance_feepaymentre_feepaymentreceipt_id_8da561d4_fk_finance_f; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_feepaymentreceipt_month_entries
    ADD CONSTRAINT finance_feepaymentre_feepaymentreceipt_id_8da561d4_fk_finance_f FOREIGN KEY (feepaymentreceipt_id) REFERENCES public.finance_feepaymentreceipt(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: finance_feepaymentreceipt finance_feepaymentre_student_id_0286c392_fk_students_; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_feepaymentreceipt
    ADD CONSTRAINT finance_feepaymentre_student_id_0286c392_fk_students_ FOREIGN KEY (student_id) REFERENCES public.students_student(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: finance_feepaymentreceipt_month_entries finance_feepaymentre_studentfeemonthentry_88f8f2aa_fk_finance_s; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_feepaymentreceipt_month_entries
    ADD CONSTRAINT finance_feepaymentre_studentfeemonthentry_88f8f2aa_fk_finance_s FOREIGN KEY (studentfeemonthentry_id) REFERENCES public.finance_studentfeemonthentry(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: finance_studentfeeledger finance_studentfeele_academic_session_id_98fdaaac_fk_school_ac; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_studentfeeledger
    ADD CONSTRAINT finance_studentfeele_academic_session_id_98fdaaac_fk_school_ac FOREIGN KEY (academic_session_id) REFERENCES public.school_academicsession(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: finance_studentfeeledger finance_studentfeele_student_id_6819ba4c_fk_students_; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_studentfeeledger
    ADD CONSTRAINT finance_studentfeele_student_id_6819ba4c_fk_students_ FOREIGN KEY (student_id) REFERENCES public.students_student(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: finance_studentfeemonthentry finance_studentfeemo_ledger_id_e4c9a9e7_fk_finance_s; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.finance_studentfeemonthentry
    ADD CONSTRAINT finance_studentfeemo_ledger_id_e4c9a9e7_fk_finance_s FOREIGN KEY (ledger_id) REFERENCES public.finance_studentfeeledger(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: school_section school_section_class_level_id_0c997e4a_fk_school_classlevel_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.school_section
    ADD CONSTRAINT school_section_class_level_id_0c997e4a_fk_school_classlevel_id FOREIGN KEY (class_level_id) REFERENCES public.school_classlevel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: students_promotionhistory students_promotionhi_from_class_id_7189d79c_fk_school_cl; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_promotionhistory
    ADD CONSTRAINT students_promotionhi_from_class_id_7189d79c_fk_school_cl FOREIGN KEY (from_class_id) REFERENCES public.school_classlevel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: students_promotionhistory students_promotionhi_from_section_id_9305de88_fk_school_se; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_promotionhistory
    ADD CONSTRAINT students_promotionhi_from_section_id_9305de88_fk_school_se FOREIGN KEY (from_section_id) REFERENCES public.school_section(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: students_promotionhistory students_promotionhi_student_id_66feb5eb_fk_students_; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_promotionhistory
    ADD CONSTRAINT students_promotionhi_student_id_66feb5eb_fk_students_ FOREIGN KEY (student_id) REFERENCES public.students_student(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: students_promotionhistory students_promotionhi_to_class_id_d284316c_fk_school_cl; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_promotionhistory
    ADD CONSTRAINT students_promotionhi_to_class_id_d284316c_fk_school_cl FOREIGN KEY (to_class_id) REFERENCES public.school_classlevel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: students_promotionhistory students_promotionhi_to_section_id_ec1f7bb7_fk_school_se; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_promotionhistory
    ADD CONSTRAINT students_promotionhi_to_section_id_ec1f7bb7_fk_school_se FOREIGN KEY (to_section_id) REFERENCES public.school_section(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: students_student students_student_current_class_id_cf5f558b_fk_school_cl; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_student
    ADD CONSTRAINT students_student_current_class_id_cf5f558b_fk_school_cl FOREIGN KEY (current_class_id) REFERENCES public.school_classlevel(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: students_student students_student_current_section_id_3239129f_fk_school_se; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_student
    ADD CONSTRAINT students_student_current_section_id_3239129f_fk_school_se FOREIGN KEY (current_section_id) REFERENCES public.school_section(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: students_student students_student_family_id_bbc9cc99_fk_students_; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students_student
    ADD CONSTRAINT students_student_family_id_bbc9cc99_fk_students_ FOREIGN KEY (family_id) REFERENCES public.students_familyhousehold(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: teachers_monthlysalarybill teachers_monthlysala_teacher_id_cc1084ca_fk_teachers_; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teachers_monthlysalarybill
    ADD CONSTRAINT teachers_monthlysala_teacher_id_cc1084ca_fk_teachers_ FOREIGN KEY (teacher_id) REFERENCES public.teachers_teacher(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: teachers_teacher teachers_teacher_salary_scale_id_e526c2c8_fk_teachers_; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teachers_teacher
    ADD CONSTRAINT teachers_teacher_salary_scale_id_e526c2c8_fk_teachers_ FOREIGN KEY (salary_scale_id) REFERENCES public.teachers_salaryscale(id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

\unrestrict ucWj8IzFgpv5QiFqd0BdHQoK4yOfgQZdwFoIbwnkZ2PLKaWdUR57dy341K6QFAN

