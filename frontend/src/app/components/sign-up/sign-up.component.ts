import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl, Validators, FormBuilder } from '@angular/forms';
import { UserHttpService } from 'src/app/services/user.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-sign-up',
  templateUrl: './sign-up.component.html',
  styleUrls: ['./sign-up.component.scss']
})
export class SignUpComponent implements OnInit {
  signUpForm: FormGroup;

  error = false;

  constructor(
    private formBuilder: FormBuilder,
    private userService: UserHttpService,
    private router: Router,
  ) { }

  ngOnInit(): void {
    this.signUpForm = this.formBuilder.group({
      username: new FormControl('', Validators.required),
      firstName: new FormControl(''),
      lastName: new FormControl(''),
      email: new FormControl('', [Validators.email]),
      password: new FormControl('', Validators.required),
    });
  }

  async signUp() {
    console.log(this.signUpForm.value);
    if (this.signUpForm.valid) {
      try {
        const response = await this.userService.signUp(
          this.signUpForm.value.username,
          this.signUpForm.value.password,
          this.signUpForm.value.email,
          this.signUpForm.value.firstName,
          this.signUpForm.value.lastName
        );
        this.error = false;
        console.log('Signup response:', response);
      } catch (error) {
        console.log('Could not Sign up');
        this.error = true;
      }
    } else {
      this.error = true;
    }
  }

  signIn() {
    this.router.navigate(['/signin']);
  }
}
