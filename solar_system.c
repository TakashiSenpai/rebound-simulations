/*
    AUTHOR: Louis-Hendrik Barboutie
    CONTACT: louis.barboutie@gmail.com
    EDITED: 09/03/2024

    PURPOSE: Simulation of the solar system with an asteroid belt
*/

#include "rebound.h"
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#include <python3.10/Python.h>

double endTime; // needs to be global for the heartbeat function

void heartbeat(struct reb_simulation *r){
    // function to print out the completion of the simulation
    if (r->steps_done % 100 == 0){
        printf("Simulation completion: %.2f %%, Steps done: %lu\r", r->t / endTime * 100, r->steps_done);
        //printf("\rCompletion: %.1f %%, Steps: %li", r->t / endTime * 100, r->steps_done);
    }
}

void save_state(char *file_path, struct reb_simulation *r){
    /*
    Save the states of the simulation to a file in non-binary format
    */
    FILE *f;
    double x, y, z, vx, vy, vz;
    printf("%s %s\n", "Saving the simulation state to", file_path);
    f = fopen(file_path, "w");
    for (int i=0; i<r->N; i++){
        x = r->particles[i].x;
        y = r->particles[i].y;
        z = r->particles[i].z;
        vx = r->particles[i].vx;
        vy = r->particles[i].vy;
        vz = r->particles[i].vz;
        fprintf(f, "%f, %f, %f, %f, %f, %f\n", x, y, z, vx, vy, vz);
    }
    fclose(f);
}

void file_copy(char *ref_file_path, char *new_file_path){
    FILE *fptr_ref, *fptr_dest;
    char temp_ch;
    
    // open files
    if ((fptr_ref = fopen(ref_file_path, "r")) == NULL){
        printf("Error opening reference file\n");
    }
    if ((fptr_dest = fopen(new_file_path, "w")) == NULL){
        printf("Error opening destination file\n");
    }

    /*
    if (fptr_ref == NULL || fptr_dest == NULL){
        Proc_err(DEF_ERR_OPT, "error opening file %s or %s", ref_file_path, new_file_path);
    }
    */

    temp_ch = fgetc(fptr_ref);     // this is the temporary char which gets filled as each new char is read, and read the first char of the reference file
    while (temp_ch != EOF){        // loop until reaching End Of File
        fputc(temp_ch, fptr_dest); // write the char into the destination file 
        temp_ch = fgetc(fptr_ref); // get next char in the reference file
    }

    // close files
    fclose(fptr_ref);
    fclose(fptr_dest);
    return;
}

int main(void){

    // ================= //
    // === VARIABLES === //
    // ================= //

    // File i/o
    FILE    *f;
    char    *line_buf = NULL;   // this has to be intialised NULL: won't be allocated unless it is NULL
    size_t   line_buf_size = 0; // this variable is written to if zero, otherwise read.
    ssize_t  line_size;         // "Signed Size_Type" : size of a buffer, but can be -1 if failed.
    
    // state variables
    double   state[6];               // positions and velocities of the bodies
    double   masses[10];             // masses of the bodies 
    double   m, x, y, z, vx, vy, vz; // placeholders for adding particles to the simulation

    // conversion factors
    double m2au = 6.6846e-12;
    double km2m = 1000;

    // Archive paths
    char workArchivePath[] = "archive.bin";
    char saveArchivePath[256];



    // ======================================== //
    // === INITIALIZATION OF THE SIMULATION === //
    // ======================================== //

    printf("Initializing the simulation ...\n");

    // initialize the rebound simulation
    struct reb_simulation *r  = reb_simulation_create();
    int nBodies = 0;
    int nAsteroids = 100000;
    int years = 1000000; 
    int nSnapshots = 10;
    int saveInterval = 2;
    int saveTime = nSnapshots * saveInterval;
    double timeStep = 10 * 86400.; // 10 days or an eightth of Mercury's orbit
    endTime = 86400. * 365 * years; // one hundred years in seconds
    sprintf(saveArchivePath, "archives/archive_%i_years_%i_particles.bin", years, nAsteroids);

    // set up simulation parameters
    r->G          = 6.6743e-11;  // change value of G to SI units
    r->dt         = timeStep;
    r->N_active   = 10;          // only the planets are not test particles
    r->heartbeat  = heartbeat;
    r->integrator = REB_INTEGRATOR_WHFAST;
    r->exact_finish_time = 0;

    // remove the last archive because rebound always appends snapshots
    (remove(workArchivePath) == 0) ? 
        printf("Archive successfully removed\n"):
        printf("warning: archive could not be removed\n");



    // ======================================= //
    // === ADD PARTICLES TO THE SIMULATION === //
    // ======================================= //

    printf("Adding bodies to the simulation ...\n");

    // manually define masses (in kg) of the planets from https://ssd.jpl.nasa.gov/planets/phys_par.html
    masses[0] = 1.32712440041279419e20 / 6.67430e-11;
    masses[1] = 0.330103e24;
    masses[2] = 4.86731e24;
    masses[3] = 5.97217e24 + 7.34767309e22;
    masses[4] = 0.641691e24; 
    masses[5] = 1898.125e24;
    masses[6] = 568.317e24;
    masses[7] = 86.8099e24;
    masses[8] = 102.4092e24;
    masses[9] = 13029.0e18;

    // open file with barycenter states
    if ((f = fopen("../spice-scripts/BarycenterStates.txt", "r")) == NULL){
        printf("Error opening the barycenter states file\n");
        return EXIT_FAILURE;
    }

    // read the file with barycenter states
    while ((line_size = getline(&line_buf, &line_buf_size, f)) != -1){
        sscanf(line_buf, "%lf %lf %lf %lf %lf %lf", &state[0], &state[1], &state[2], &state[3], &state[4], &state[5]);
        if( line_size <= 0 ){
            printf("Reached end of file, or otherwise failed to read. Returned: %i\n", (int)line_size);
            break; 
        }

        // add solar system planets
        // convert position and velocities from km/s to m/s
        m  = masses[nBodies];
        x  = state[0] * km2m;
        y  = state[1] * km2m;
        z  = state[2] * km2m;
        vx = state[3] * km2m;
        vy = state[4] * km2m;
        vz = state[5] * km2m;
        reb_simulation_add_fmt(r, "m x y z vx vy vz", m, x, y, z, vx, vy, vz);
        nBodies++;
    }
    fclose(f);

    printf("Adding asteroids to simulation ...\n");
    
    // Use python to generate the asteroid states
    char cmdStr1[] = "python3 randAstOrbitGen.py "; 
    char cmdStr2[64];
    sprintf(cmdStr2, "%d", nAsteroids);
    strcat(cmdStr1, cmdStr2);
    system(cmdStr1);

    // Open the file with the asteroid states
    if ((f = fopen("asteroidStates.csv", "r")) == NULL){
        printf("Error opening the asteroid states file\n");
        return EXIT_FAILURE;
    }

    // read the file line by line 
    while ((line_size = getline(&line_buf, &line_buf_size, f)) != -1){
        sscanf(line_buf, "%lf %lf %lf %lf %lf %lf", &state[0], &state[1], &state[2], &state[3], &state[4], &state[5]);
        if( line_size <= 0 ){
            printf("Reached end of file, or otherwise failed to read. Returned: %i\n", (int)line_size);
            break;
        }

        // add asteroids
        x  = state[0];
        y  = state[1];
        z  = state[2];
        vx = state[3];
        vy = state[4];
        vz = state[5];
        reb_simulation_add_fmt(r, "x y z vx vy vz", x, y, z, vx, vy, vz);
    }
    fclose(f);
    
    // move the origin to center of mass so that the simulation doesn't drift away
    reb_simulation_move_to_com(r);
    
    // Save the initial conditions to csv file
    save_state("input.csv", r);



    // ============================== //
    // === RUNNING THE SIMULATION === //
    // ============================== //

    printf("Running the simulation ...\n");
    
    // Integrate with snapshot saving 
    printf("Saving the initial snapshots ...\n");
    reb_simulation_save_to_file_interval(r, workArchivePath, saveInterval * r->dt);
    reb_simulation_integrate(r, saveTime);
    printf("\n");

    // Integrate without snapshots for a loooong time
    printf("Time travelling to the future ...\n");
    reb_simulation_save_to_file_interval(r, workArchivePath, 0);
    reb_simulation_integrate(r, endTime);
    printf("\n");

    // Save more snapshots of the end of the simulation
    printf("Saving the final snapshots ...\n");
    reb_simulation_save_to_file_interval(r, workArchivePath, saveInterval * r->dt);
    reb_simulation_integrate(r, endTime + saveTime);
    printf("\n");
    


    // ========================================= //
    // === POST PROCESSING OF THE SIMULATION === //
    // ========================================= //

    // Save the final conditions to csv file
    save_state("output.csv", r);
   
    // run the plotting script
    system("python3 kirkwood.py");

    // free the memory of the simulation after being done
    reb_simulation_free(r);

    // archive the simulation
    file_copy(workArchivePath, saveArchivePath);

    return EXIT_SUCCESS;
}