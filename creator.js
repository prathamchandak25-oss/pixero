


document.addEventListener('DOMContentLoaded', function () {
    // Tab switching
    const tabs = document.querySelectorAll('.tab');
    const creatorTypeInput = document.getElementById('creator-type');
    const photographerServices = document.getElementById('photographer-services');
    const editorServices = document.getElementById('editor-services');

    tabs.forEach(tab => {
        tab.addEventListener('click', function () {
            tabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');

            const type = this.getAttribute('data-type');
            creatorTypeInput.value = type;

            if (type === 'photographer') {
                photographerServices.classList.remove('hidden');
                editorServices.classList.add('hidden');
            } else {
                photographerServices.classList.add('hidden');
                editorServices.classList.remove('hidden');
            }
        });
    });

    // Profile photo upload
    const profilePhotoInput = document.getElementById('profile-photo');
    const photoPreview = document.getElementById('photo-preview');
    const uploadPhotoBtn = document.getElementById('upload-photo-btn');

    uploadPhotoBtn.addEventListener('click', function () {
        profilePhotoInput.click();
    });

    profilePhotoInput.addEventListener('change', function () {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                photoPreview.innerHTML = `<img src="${e.target.result}" alt="Profile Preview">`;
            };
            reader.readAsDataURL(file);
        }
    });

    // Portfolio links
    const addPortfolioBtn = document.getElementById('add-portfolio');
    const portfolioLinks = document.getElementById('portfolio-links');

    addPortfolioBtn.addEventListener('click', function () {
        const portfolioItem = document.createElement('div');
        portfolioItem.className = 'portfolio-item';
        portfolioItem.innerHTML = `
            <input type="url" name="portfolio[]" placeholder="https://example.com/your-work">
            <span class="remove-item">Remove</span>
        `;
        portfolioLinks.appendChild(portfolioItem);

        // Add event listener to the remove button
        portfolioItem.querySelector('.remove-item').addEventListener('click', function () {
            portfolioLinks.removeChild(portfolioItem);
        });
    });

    // Service pricing logic
    const serviceCheckboxes = document.querySelectorAll('input[name="services"]');

    serviceCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            const priceInput = this.parentElement.querySelector('input[type="number"]');
            if (this.checked) {
                priceInput.required = true;
            } else {
                priceInput.required = false;
                priceInput.value = '';
            }
        });
    });

    // Form submission
    const form = document.getElementById('creator-form');
    const successMessage = document.getElementById('success-message');

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        // Validate that at least one service is selected
        const creatorType = creatorTypeInput.value;
        const relevantServices = creatorType === 'photographer' ?
            document.querySelectorAll('#photographer-services input[type="checkbox"]:checked') :
            document.querySelectorAll('#editor-services input[type="checkbox"]:checked');

        if (relevantServices.length === 0) {
            alert('Please select at least one service to offer');
            return;
        }

        // Collect form data
        const formData = {
            creator_type: creatorTypeInput.value,
            full_name: document.getElementById('full-name').value,
            email: document.getElementById('email').value,
            phone: document.getElementById('phone').value,
            location: document.getElementById('location').value,
            experience: document.getElementById('experience').value,
            equipment: document.getElementById('equipment').value,
            bio: document.getElementById('bio').value,
            website: document.getElementById('website').value,
            instagram: document.getElementById('instagram').value,
            availability: document.getElementById('availability').value,
            services: [],
            portfolio: [],
            payment_methods: []
        };

        // Collect services and prices in the proper format
        const selectedServices = document.querySelectorAll('input[name="services"]:checked');
        selectedServices.forEach(service => {
            const serviceValue = service.value;
            const priceInput = service.parentElement.querySelector('input[type="number"]');
            let price = 0;
            
            if (priceInput && priceInput.value) {
                price = parseFloat(priceInput.value);
            }
            
            // Format service object properly with service_name, price, and unit
            formData.services.push({
                service_name: serviceValue,
                price: price,
                unit: "per session" // Default unit - adjust as needed
            });
        });

        // Collect portfolio links
        const portfolioInputs = document.querySelectorAll('input[name="portfolio[]"]');
        portfolioInputs.forEach(input => {
            if (input.value.trim()) {
                formData.portfolio.push(input.value);
            }
        });

        // Collect payment methods
        const paymentMethods = document.querySelectorAll('input[name="payment_methods"]:checked');
        paymentMethods.forEach(method => {
            formData.payment_methods.push(method.value);
        });

        try {
            // Send data to server
            const response = await fetch('/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (response.ok) {
                // If registration successful, handle profile photo upload if selected
                const profilePhotoFile = document.getElementById('profile-photo').files[0];
                if (profilePhotoFile && result.creator_id) {
                    const photoFormData = new FormData();
                    photoFormData.append('profile_photo', profilePhotoFile);
                    photoFormData.append('creator_id', result.creator_id);

                    await fetch('/upload_profile_photo', {
                        method: 'POST',
                        body: photoFormData
                    });
                }

                // Reset form and show success message
                form.reset();
                photoPreview.innerHTML = '<span>Upload Photo</span>';
                successMessage.classList.remove('hidden');
                setTimeout(() => {
                    successMessage.classList.add('hidden');
                }, 5000);
            } else {
                alert(`Registration failed: ${result.error}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again later.');
        }
    });
});