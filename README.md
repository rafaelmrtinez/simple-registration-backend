# simple-registration-backend

## Table of Contents

- [Introduction](#introduction)
- [Project Structure](#project-structure)
- [Module Overview](#module-overview)
	- [Views](#views)
	- [Models](#models)
	- [Serializers](#serializers)
	- [URLs](#urls)
	- [Utils](#utils)
- [Notes](#notes)

## Introduction

This backend is built for simulation purposes only. It is intended to run in a local Kubernetes cluster so that cluster behavior, service wiring, and application flows can be practiced in a controlled environment. It is not meant to be deployed to production.

That said, the project can be configured to resemble real-world application patterns. The goal is to provide a realistic but safe backend for testing deployment workflows, service discovery, and API interactions without the operational expectations of a production system.

## Project Structure

The project is organized as a small Django backend with a single registration app. The app exposes API endpoints for creating and listing user profiles, along with a utility layer for generating and decoding derived identifiers.

## Module Overview

### Views

The main view lives in [registration/views.py](registration/views.py). It defines the `UserProfile` API view and handles two primary actions:

- `GET`: Returns all stored user profiles, with optional searching through the `q` query parameter.
- `POST`: Creates a new user profile from request data.

The `GET` handler supports several search modes. If the query begins with `U-`, the view attempts to decode it back to a raw database ID and filter by that record. If the query contains two words, it treats them as first name and last name. Otherwise, it searches across first name, last name, mobile number, and email.

### Models

The model is defined in [registration/models.py](registration/models.py). It contains the `UserProfile` model, which stores the user data managed by the API.

Important fields include:

- `username`: unique user name
- `first_name` and `last_name`: profile names
- `date_of_birth`: profile date of birth
- `mobile_number`: unique contact number
- `email`: unique email address
- `password`: stored password field
- `created_at`: auto-generated creation timestamp
- `entered_by_id`: identifier for the actor or process that created the profile

The model orders records by creation time and provides a readable string representation using the username and email.

### Serializers

The serializers are defined in [registration/serializers.py](registration/serializers.py). They provide request and response shaping for the API.

- `UserProfileSerializer` is used for creating and updating `UserProfile` records. It validates the incoming profile fields and maps them into model instances.
- `UserProfileListSerializer` is used for read-only listing. It exposes a derived `id` instead of the raw database primary key by calling the ID encoding utility.

The listing serializer also includes the stored profile fields and exposes `entered_by_id` as the `entered_by` field in responses.

### URLs

Routing is split between the project URL configuration and the app URL configuration.

The project-level URL configuration lives in [myapp/urls.py](myapp/urls.py). It wires up:

- Django admin at `/admin/`
- Django REST Framework login endpoints at `/api-auth/`
- The registration app routes under `/user/`

The app-level URL configuration lives in [registration/urls.py](registration/urls.py). It defines:

- `/user/register/` for the profile API view
- `/user/profiles/` for the profile listing API view

Both routes currently point to the same `UserProfile` API view, which means the behavior is controlled by the HTTP method rather than different view classes.

### Utils

Utility functions are defined in [registration/utils.py](registration/utils.py). This module is responsible for derived ID handling.

- `encode_id(pk)` converts a raw integer primary key into a derived `U-...` string that includes the current year and a Base64-encoded payload.
- `decode_id(derived)` performs the reverse operation and returns the original integer primary key.

These helpers are used to hide raw database IDs in API responses while still allowing search and lookup by derived identifier.

## Notes

- This project is intentionally lightweight and focused on local simulation.
- It is suitable for experimenting with container orchestration, service configuration, and API behavior.
- It should not be treated as a production-ready authentication or profile management system.
