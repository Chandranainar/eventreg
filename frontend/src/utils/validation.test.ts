import { describe, expect, it } from "vitest";

import { validateRegistration } from "./validation";

const valid = {
  full_name: "Sample Person",
  phone_number: "+91 9876543210",
  additional_contact_number: "",
  email: "sample@example.com",
  educational_qualification: "MBA",
  age: 30,
  current_city: "Chennai",
  gender: "Male",
  profession: "Technology Company",
  business_company_name: "Sample Technologies",
  attendance: "Will attend for sure",
  food_preference: "Vegetarian",
  alpha_alumni: "No",
  studied_standard: "",
  year_of_passing: "",
  consent_given: true
};

describe("validateRegistration", () => {
  it("accepts valid registration values", () => {
    expect(validateRegistration(valid)).toEqual({});
  });

  it("rejects invalid phone, age, email and missing required choices", () => {
    const errors = validateRegistration({
      ...valid,
      age: 101,
      current_city: "",
      gender: "",
      email: "bad",
      phone_number: "123",
      profession: "",
      attendance: "",
      food_preference: "",
      alpha_alumni: ""
    });

    expect(errors.age).toBeTruthy();
    expect(errors.current_city).toBeTruthy();
    expect(errors.gender).toBeTruthy();
    expect(errors.email).toBeTruthy();
    expect(errors.phone_number).toBeTruthy();
    expect(errors.profession).toBeTruthy();
    expect(errors.attendance).toBeTruthy();
    expect(errors.food_preference).toBeTruthy();
    expect(errors.alpha_alumni).toBeTruthy();
  });

  it("requires school details for Alpha alumni", () => {
    const errors = validateRegistration({
      ...valid,
      alpha_alumni: "Yes"
    });

    expect(errors.studied_standard).toBeTruthy();
    expect(errors.year_of_passing).toBeTruthy();
  });
});
