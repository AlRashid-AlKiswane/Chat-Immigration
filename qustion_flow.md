        questions: [
            {
                id: 'marital_status',
                title: 'What is your marital status?',
                subtitle: 'Please select your current marital status',
                type: 'radio',
                options: [
                    { value: 'never_married', label: 'Never Married/Single' },
                    { value: 'married', label: 'Married' },
                    { value: 'common_law', label: 'Common-Law' },
                    { value: 'divorced', label: 'Divorced/Separated' },
                    { value: 'legally_separated', label: 'Legally Separated' },
                    { value: 'annulled', label: 'Annulled Marriage' },
                    { value: 'widowed', label: 'Widowed' }
                ]
            },
            {
                id: 'spouse_citizen',
                title: 'Is your spouse or common-law partner a citizen or permanent resident of Canada?',
                subtitle: 'This affects your points calculation',
                type: 'radio',
                condition: (answers) => ['married', 'common_law'].includes(answers.marital_status),
                options: [
                    { value: 'yes', label: 'Yes' },
                    { value: 'no', label: 'No' }
                ]
            },
            {
                id: 'spouse_coming',
                title: 'Will your spouse or common-law partner come with you to Canada?',
                subtitle: 'This determines if they are considered accompanying',
                type: 'radio',
                condition: (answers) => ['married', 'common_law'].includes(answers.marital_status) && answers.spouse_citizen === 'no',
                options: [
                    { value: 'yes', label: 'Yes' },
                    { value: 'no', label: 'No' }
                ]
            },
            {
                id: 'age',
                title: 'How old are you?',
                subtitle: 'Enter your age in years',
                type: 'number',
                min: 17,
                max: 65
            },
            {
                id: 'education_level',
                title: 'What is your level of education?',
                subtitle: 'Select the highest level of education you have completed',
                type: 'radio',
                options: [
                    { value: 'less_than_secondary', label: 'Less than secondary school (high school)' },
                    { value: 'secondary_diploma', label: 'Secondary diploma (high school graduation)' },
                    { value: 'one_year_post_secondary', label: 'One-year diploma, certificate, or credential from a university, college, trade or technical school' },
                    { value: 'two_year_post_secondary', label: 'Two-year program at a university, college, trade or technical school' },
                    { value: 'bachelor_or_three_year_post_secondary_or_more', label: 'Bachelor\'s degree or three or more year program at a university, college, trade or technical school' },
                    { value: 'two_or_more_post_secondary_one_three_year', label: 'Two or more certificates, diplomas, or degrees (at least one three years or more)' },
                    { value: 'masters_or_professional_degree', label: 'Master\'s degree or professional degree needed to practice in a licensed profession' },
                    { value: 'phd', label: 'Doctoral level university degree (PhD)' }
                ]
            },
            {
                id: 'canada_education',
                title: 'Have you earned a Canadian degree, diploma or certificate?',
                subtitle: 'This refers to credentials earned in Canada',
                type: 'radio',
                options: [
                    { value: 'yes', label: 'Yes' },
                    { value: 'no', label: 'No' }
                ]
            },
            {
                id: 'education_eca',
                title: 'Choose the best answer to describe this level of education',
                subtitle: 'Select the level that best matches your Canadian credential',
                type: 'radio',
                condition: (answers) => answers.canada_education === 'yes',
                options: [
                    { value: 'secondary_or_less', label: 'Secondary school (high school) credential or less' },
                    { value: 'one_or_two_diploma', label: 'One-year or two-year diploma or certificate' },
                    { value: 'degree_three_years_or_more', label: 'Degree, diploma or certificate of three years or more' }
                ]
            },
            {
                id: 'language_test_recent',
                title: 'Official Language Test - Are your test results less than two years old?',
                subtitle: 'Language test results must be less than 2 years old to be valid',
                type: 'radio',
                options: [
                    { value: 'yes', label: 'Yes, my test results are less than 2 years old' },
                    { value: 'no', label: 'No, my test results are 2 years old or older' },
                    { value: 'no_test', label: 'I have not taken a language test' }
                ]
            },
            {
                id: 'first_language_test',
                title: 'Which language test did you take for your first official language?',
                subtitle: 'Select the test you took for your stronger official language',
                type: 'radio',
                condition: (answers) => answers.language_test_recent === 'yes',
                options: [
                    { value: 'IELTS', label: 'IELTS - International English Language Testing System' },
                    { value: 'CELPIP-G', label: 'CELPIP-G - Canadian English Language Proficiency Index Program' },
                    { value: 'PTE CORE', label: 'PTE Core - Pearson Test of English Core' },
                    { value: 'TEF CANADA', label: 'TEF Canada - Test d\'évaluation de français' },
                    { value: 'TCF CANADA', label: 'TCF Canada - Test de connaissance du français' }
                ]
            },
            {
                id: 'first_language_scores',
                title: 'Enter your test scores for your first official language',
                subtitle: 'Enter the exact scores from your official test results',
                type: 'scores',
                condition: (answers) => answers.language_test_recent === 'yes' && answers.first_language_test
            },
            {
                id: 'second_language_test',
                title: 'Do you have test results for your second official language?',
                subtitle: 'If you took a test for your second official language, select it here',
                type: 'radio',
                condition: (answers) => answers.language_test_recent === 'yes',
                options: [
                    { value: 'not_applicable', label: 'Not applicable - I did not take a test for my second official language' },
                    { value: 'IELTS', label: 'IELTS - International English Language Testing System' },
                    { value: 'CELPIP-G', label: 'CELPIP-G - Canadian English Language Proficiency Index Program' },
                    { value: 'PTE CORE', label: 'PTE Core - Pearson Test of English Core' },
                    { value: 'TEF CANADA', label: 'TEF Canada - Test d\'évaluation de français' },
                    { value: 'TCF CANADA', label: 'TCF Canada - Test de connaissance du français' }
                ]
            },
            {
                id: 'second_language_scores',
                title: 'Enter your test scores for your second official language',
                subtitle: 'Enter the exact scores from your official test results',
                type: 'scores',
                condition: (answers) => answers.second_language_test && answers.second_language_test !== 'not_applicable'
            },
            {
                id: 'canadian_work_experience',
                title: 'In the last 10 years, how many years of skilled work experience in Canada do you have?',
                subtitle: 'Count only skilled work experience (NOC TEER 0, 1, 2, or 3)',
                type: 'radio',
                options: [
                    { value: '0', label: 'None or less than a year' },
                    { value: '1', label: '1 year' },
                    { value: '2', label: '2 years' },
                    { value: '3', label: '3 years' },
                    { value: '4', label: '4 years' },
                    { value: '5_or_more', label: '5 years or more' }
                ]
            },
            {
                id: 'foreign_work_experience',
                title: 'In the last 10 years, how many years of foreign skilled work experience do you have?',
                subtitle: 'Count skilled work experience outside Canada',
                type: 'radio',
                options: [
                    { value: '0', label: 'None or less than a year' },
                    { value: '1', label: '1 year' },
                    { value: '2', label: '2 years' },
                    { value: '3', label: '3 years or more' }
                ]
            },
            {
                id: 'trade_certificate',
                title: 'Do you have a certificate of qualification from a Canadian province, territory or federal body?',
                subtitle: 'This applies to regulated trades',
                type: 'radio',
                options: [
                    { value: 'yes', label: 'Yes' },
                    { value: 'no', label: 'No' }
                ]
            },
            {
                id: 'job_offer',
                title: 'Do you have a valid job offer supported by a Labour Market Impact Assessment (if needed)?',
                subtitle: 'The job offer must be valid and supported by LMIA when required',
                type: 'radio',
                options: [
                    { value: 'yes', label: 'Yes' },
                    { value: 'no', label: 'No' }
                ]
            },
            {
                id: 'noc_teer',
                title: 'Which NOC TEER category is the job offer?',
                subtitle: 'Find out your job\'s TEER category if you don\'t know',
                type: 'radio',
                condition: (answers) => answers.job_offer === 'yes',
                options: [
                    { value: 'noc_teer_0_major_group_00', label: 'NOC TEER 0 - Major group 00' },
                    { value: 'noc_teer_1_2_or_3_or_any_teer_0_than_major_group_00', label: 'NOC TEER 1, 2, or 3, or any TEER 0 other than Major group 00' },
                    { value: 'noc_teer_4_or_5', label: 'NOC TEER 4 or 5' }
                ]
            },
            {
                id: 'do_have_nomination',
                title: 'Do you have a nomination certificate from a province or territory?',
                subtitle: 'Provincial Nominee Program (PNP) nomination',
                type: 'radio',
                options: [
                    { value: 'yes', label: 'Yes' },
                    { value: 'no', label: 'No' }
                ]
            },
            {
                id: 'siblings',
                title: 'Do you or your spouse or common-law partner have at least one brother or sister living in Canada?',
                subtitle: 'The brother or sister must be a Canadian citizen or permanent resident, and be 18 years or older',
                type: 'radio',
                options: [
                    { value: 'yes', label: 'Yes' },
                    { value: 'no', label: 'No' }
                ]
            },
            {
                id: 'spouse_education',
                title: 'What is the highest level of education for which your spouse or common-law partner has earned a Canadian degree, diploma or certificate; or had an Educational Credential Assessment (ECA)?',
                subtitle: 'ECAs must be from an approved agency, in the last five years',
                type: 'radio',
                condition: (answers) => answers.spouse_coming === 'yes',
                options: [
                    { value: 'less_than_secondary', label: 'Less than secondary school (high school)' },
                    { value: 'secondary_diploma', label: 'Secondary diploma (high school graduation)' },
                    { value: 'one_year_post_secondary', label: 'One-year diploma, certificate, or credential from a university, college, trade or technical school' },
                    { value: 'two_year_post_secondary', label: 'Two-year program at a university, college, trade or technical school' },
                    { value: 'bachelor_or_three_year_post_secondary_or_more', label: 'Bachelor\'s degree or three or more year program at a university, college, trade or technical school' },
                    { value: 'two_or_more_post_secondary_one_three_year', label: 'Two or more certificates, diplomas, or degrees (at least one three years or more)' },
                    { value: 'masters_or_professional_degree', label: 'Master\'s degree or professional degree needed to practice in a licensed profession' },
                    { value: 'phd', label: 'Doctoral level university degree (PhD)' }
                ]
            },
            {
                id: 'spouse_experience',
                title: 'In the last 10 years, how many years of skilled work experience in Canada does your spouse/common-law partner have?',
                subtitle: 'It must have been paid, full-time (or an equal amount in part-time), and in one or more NOC TEER category 0, 1, 2, or 3 jobs',
                type: 'radio',
                condition: (answers) => answers.spouse_coming === 'yes',
                options: [
                    { value: '0', label: 'None or less than a year' },
                    { value: '1', label: '1 year' },
                    { value: '2', label: '2 years' },
                    { value: '3', label: '3 years' },
                    { value: '4', label: '4 years' },
                    { value: '5', label: '5 years or more' }
                ]
            },
            {
                id: 'spouse_language_test',
                title: 'Did your spouse or common-law partner take a language test?',
                subtitle: 'Test results must be less than two years old',
                type: 'radio',
                condition: (answers) => answers.spouse_coming === 'yes',
                options: [
                    { value: 'not_applicable', label: 'Not applicable - did not take a language test' },
                    { value: 'IELTS', label: 'IELTS - International English Language Testing System' },
                    { value: 'CELPIP-G', label: 'CELPIP-G - Canadian English Language Proficiency Index Program' },
                    { value: 'PTE CORE', label: 'PTE Core - Pearson Test of English Core' },
                    { value: 'TEF CANADA', label: 'TEF Canada - Test d\'évaluation de français' },
                    { value: 'TCF CANADA', label: 'TCF Canada - Test de connaissance du français' }
                ]
            },
            {
                id: 'spouse_language_scores',
                title: 'Enter your spouse\'s test scores for their official language',
                subtitle: 'Enter the exact scores from their official test results',
                type: 'scores',
                condition: (answers) => answers.spouse_language_test && answers.spouse_language_test !== 'not_applicable'
            }
        ],

        // Score presets for language tests
        scorePresets: {
            'IELTS': {
                listening: [9.0, 8.5, 8.0, 7.5, 7.0, 6.5, 6.0, 5.5, 5.0, 4.5, 4.0],
                speaking: [9.0, 8.5, 8.0, 7.5, 7.0, 6.5, 6.0, 5.5, 5.0, 4.5, 4.0],
                reading: [9.0, 8.5, 8.0, 7.5, 7.0, 6.5, 6.0, 5.5, 5.0, 4.5, 4.0],
                writing: [9.0, 8.5, 8.0, 7.5, 7.0, 6.5, 6.0, 5.5, 5.0, 4.5, 4.0]
            },
            'CELPIP-G': {
                listening: [12, 11, 10, 9, 8, 7, 6, 5, 4, 3],
                speaking: [12, 11, 10, 9, 8, 7, 6, 5, 4, 3],
                reading: [12, 11, 10, 9, 8, 7, 6, 5, 4, 3],
                writing: [12, 11, 10, 9, 8, 7, 6, 5, 4, 3]
            },
            'PTE CORE': {
                reading: ['88-90', '78-87', '69-77', '60-68', '51-59', '42-50', '33-41', '24-32'],
                writing: ['90', '88-89', '79-87', '69-78', '60-68', '51-59', '41-50', '32-40'],
                listening: ['89-90', '82-88', '71-81', '60-70', '50-59', '39-49', '28-38', '18-27'],
                speaking: ['89-90', '84-88', '76-83', '68-75', '59-67', '51-58', '42-50', '34-41']
            },
            'TEF CANADA': {
                reading: ['546-699', '503-545', '462-502', '434-461', '393-433', '352-392', '306-351'],
                writing: ['558-699', '512-557', '472-511', '428-471', '379-427', '330-378', '268-329'],
                listening: ['546-699', '503-545', '462-502', '434-461', '393-433', '352-392', '306-351'],
                speaking: ['556-699', '518-555', '494-517', '456-493', '422-455', '387-421', '328-386']
            },
            'TCF CANADA': {
                reading: ['549-699', '524-548', '499-523', '453-498', '406-452', '375-405', '342-374'],
                writing: ['16-20', '14-15', '12-13', '10-11', '7-9', '6', '4-5'],
                listening: ['549-699', '523-548', '503-522', '458-502', '398-457', '369-397', '331-368'],
                speaking: ['16-20', '14-15', '12-13', '10-11', '7-9', '6', '4-5']
            }
        },
