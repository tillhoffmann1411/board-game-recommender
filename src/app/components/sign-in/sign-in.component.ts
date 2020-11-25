import { Component, OnInit } from '@angular/core';
import { FormBuilder, Validators, FormGroup, FormControl } from '@angular/forms';
import { AuthStore } from '../../storemanagement/auth.store';
import { Router } from '@angular/router';

@Component({
  selector: 'app-sign-in',
  templateUrl: './sign-in.component.html',
  styleUrls: ['./sign-in.component.scss']
})
export class SignInComponent implements OnInit {
  signInForm: FormGroup;

  error = false;

  constructor(
    private formBuilder: FormBuilder,
    private authService: AuthStore,
    private router: Router,
  ) { }

  ngOnInit(): void {
    this.signInForm = this.formBuilder.group({
      email: new FormControl('', [Validators.required, Validators.email]),
      password: new FormControl('', Validators.required),
    });

    this.authService.getError.subscribe(error => {
      if (error) {
        this.error = true;
      }
    });
  }

  async signIn() {
    if (this.signInForm.valid) {
      await this.authService.signIn(this.signInForm.value.email, this.signInForm.value.password);
    } else {
      this.error = true;
    }
  }

  signUp() {
    this.router.navigate(['/signup']);
  }

}
