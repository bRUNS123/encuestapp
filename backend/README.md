- API:

    - APPOINTMENTS
        - FLUJO REAGENDAMIENTO
        - FLUJO DEVOLUCION PLATA

    ~~- CATEGORIES~~

    - PRODUCTS
        - PACKS wp_h9jkmw_amelia_packages
        - "este producto esta disponible en pack"
        ~~- pack por ejemplo con sesiones de nutri y de psicologia, citas asociadas~~
    
    - INVOICE
        - INVOICE(ITEM?) DISCOUNT / CUPONES. el descuento o cupon es al producto
        - PAY INVOICE
            ~~- MercadoPago (Integrar)~~
            - Stripe (Integrar)
        ~~- CREATE TRIBUTARY DOCUMENT~~
            ~~- Openfactura API (Integrar)~~
        - FLUJO DEVOLUCION PLATA

    - PROFILES
        - USER AUTENTICATION/AUTORIZATHIO
            - https://www.django-rest-framework.org/tutorial/4-authentication-and-permissions/
            - RECOVER PASSWORD

        - NON WORKING DAYS
        ~~- WORK SCHEDULE~~

        - PRODUCT PROFILES
        ~~- SERVICE CATEGORY~~


    - EMAILING amelia_notifications
        - Mailgun (Integrar)
        - Lista de emails a enviar
            - PARA PACIENTES
                - Before 1h presencial
                - After presencial
                - Confirm presencial
                
                - After online
                - Nutri control reminder
                - Nutri evaluation
                - 30 min before online
                - appointment Aproved/Confirmed 
                - appointment Cancelled 
                - appointment Rescheduled 
                - appointment reminder
                - appointment after
                - Pack buyed
                - Pack cancelled

            - PARA TRABAJADORES
                - appointment approved
                - appointment cancelled
                - appointment rescheduled
                - pack buyed
                - pack cancelled

            - CORREOS POST SEGUN NUMERO DE SESION




- ADMIN PANEL

    - (V) Dashboard con resumenes de ventas/appointments del ¿día?
    
    - Profiles (HR)

        - Add new customer is_customer
        - Add new staff member is_staff

        - Add new professional is_provider
            - Campos necesarios
                - rut
                - postgrados (fk)
                - experiencias (fk)
                - picture (imagefield)
                - video (filefield)
                - categorias?
                - status
            - Services (M2M)
            - WorkSchedule
            - Non working Days



    - Appointmments
        - (V) AppointmentsList
            - Initial: start & end _date = today. order by start_date professional_name
            - Table: Professional, Customer, Title (Adultos?), Duration

        - (V) Sesion (AppointmentDetail)
            - InvoiceLink
            - Is part of pack? Pack price

    - Companies (B2B)
        - Add company
        - Import workers
    
    - Invoices (Woocommerce)
        - (V) InvoicesList
        - (V) InvoiceDetail
                - Date
                - Billing
                    - Name (PROFILE FK?)
                    - Email (PROFILE FK?)
                    - Phone (PROFILE FK?)
                    - Type (Boleta Electrónica Exenta (41))
                    - Folio (Openfactura) 
                - Mercadopago status
                - Items
                    - If appointment
                        - Start time
                        - Customer time
                        - Service category
                        - Professional
                        - n° of people
                        - RUT
                - Subtotal - Total
                - Payment status
                - Refund?
                - Invoice notes (fk for every status change)
        - Pay invoice vuelta completa (beta online)


    - Services 


- BUSINESS OWNER PANEL
    - Inicio
        - Resumenes
    
    - (V) Lista de trabajadores (WorkersList)
    - Asignar sesiones a trabajadores
    - Importar trabajadores

- PROFESSIONAL PANEL
    - (V) Inicio
        - Sesiones de hoy
        - Noticias

    - (V) Lista de pacientes (PatientsList)
        - Lista de sesiones por paciente
            - Dar de alta
            - Derivar


    - (V) Lista de sesiones (AppointmentsList)
            - Llamar paciente
    
    - (V) Sesion (AppointmentDetail)
        - SESION IFRAME
        - INASISTENCIA NPO NPE
        - NOTES
    
    - DOCUMENTOS ?
    - Reagendamiento interno. ¿A qué corresponde? ¿Por qué existe?

- PATIENT PANEL
    - RESCHEDULE


- WORDPRESS APPOINTMENT PLUGIN
    - CAJA AGENDAMIENTO
        - Add new patient (On first appointment) - Flujo? Poner que si ya tiene citas anteriores, que se loguee?
    - Que opciones se le puede pasar a la caja?

