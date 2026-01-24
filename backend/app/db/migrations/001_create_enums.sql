-- Create enum types for the database schema

-- Assignee type enum for task assignments
CREATE TYPE assignee_type AS ENUM ('user', 'agent', 'unassigned');

-- Assignment risk level enum
CREATE TYPE assignment_risk AS ENUM ('low', 'medium', 'high');

-- User level enum for profiles
CREATE TYPE level AS ENUM ('junior', 'mid', 'senior', 'staff', 'principal');

-- Team member role enum (matches UserRole in Python)
CREATE TYPE team_role AS ENUM ('admin', 'manager', 'member', 'viewer');
