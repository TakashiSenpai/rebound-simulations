#include "rebound.h"
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#include <python3.10/Python.h>

double endTime;
void heartbeat(struct reb_simulation *r){
    if (r->steps_done % 100 == 0){
        printf("\rCurrent simulation completion: %f %%, simulation steps: %li", r->t / endTime * 100, r->steps_done);
    }
}

float frand(float range){
    float randf = rand() / (float) RAND_MAX; // random number between 0 and 1
    randf = randf * range - range / 2;
    return randf;
}

int main(void){
    FILE    *f = fopen("../spice-scripts/BarycenterStates.txt", "r");
    char    *line_buf = NULL;  //this has to be intialised NULL: won't be allocated unless it is NULL
    size_t   line_buf_size = 0; //this variable is written to if zero, otherwise read.
    ssize_t  line_size; //"Signed Size_Type" : size of a buffer, but can be -1 if failed.
    double   state[6];
    double   masses[10]; // masses of the bodies 
    double   m, x, y, z, vx, vy, vz; // placeholders for adding particles to the simulation
    bool CgenAsteroids = false;

    if (f == NULL){
        printf("Error opening the file\n");
        return EXIT_FAILURE;
    }

    if (remove("archive.bin") != 0){
       printf("warning: archive could not be removed\n");
    }

    // initialize the rebound simulation
    struct reb_simulation *r  = reb_simulation_create();

    // change value of G to SI units
    r->G = 6.6743e-11;

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

    // Add planets to the simulation
    double m2au = 6.6846e-12;
    int count = 0;
    while ((line_size = getline(&line_buf, &line_buf_size, f)) != -1){

        // read the file with barycenter states
        sscanf(line_buf, "%lf %lf %lf %lf %lf %lf", &state[0], &state[1], &state[2], &state[3], &state[4], &state[5]);
        if( line_size <= 0 ){
            printf("Reached end of file, or otherwise failed to read. Returned: %i\n", (int)line_size);
            break; //exit the loop
        }

        // add solar system planets
        // convert position and velocities from km/s to m/s
        m = masses[count];
        x = state[0] * 1000;
        y = state[1] * 1000;
        z = state[2] * 1000;
        vx = state[3] * 1000;
        vy = state[4] * 1000;
        vz = state[5] * 1000;
        // printf("r = %f AU\n", pow(pow(x,2) + pow(y,2) + pow(z,2),0.5) * m2au);
        // printf("v = %f m/s\n\n", pow(pow(vx,2) + pow(vy,2) + pow(vz,2),0.5));
        reb_simulation_add_fmt(r, "m x y z vx vy vz", m, x, y, z, vx, vy, vz);
        count++;
    }
    fclose(f);

    int nAsteroids = 100;
    if (CgenAsteroids == true){
        // add asteroid belt
        // min distance : 1.6 A.U. (after Mars Orbit)
        // max distance: 5 A.U. (before Jupiter orbit)
        double au2km      = 149597870.7;
        double minDist    = 1.6 * au2km * 1000;
        double maxDist    = 5 * au2km * 1000;
        double avgDist    = (maxDist + minDist ) / 2;
        double ranDist;

        // put asteroids on uniform circular motion and then offset position and velocity 
        // with random numbers to produce keplerian orbits
        
        // printf("error here 1?\n");
        // double pi = atan(1) * 4;
        // printf("error here 2\n?");

        printf("Computing circular motion parameters ... ");
        #define PI 3.1415926
        double dtheta = 2 * PI / nAsteroids;
        double vCircular(double x, double y, double z){
            return sqrt((r->G) * masses[0] / pow(pow(x,2) + pow(y,2) + pow(z,2),0.5));
        }
        printf("Done!\n");

        // initialize random number generator
        int seed = 42;
        srand(seed);
        double randRange = maxDist - minDist;
        
        printf("Adding asteroids to the simulation ... ");
        for (int i=0; i<nAsteroids; i++){
            double angle = i * dtheta;
            ranDist = frand(randRange);
            x = (avgDist + ranDist) * cos(angle);
            y = (avgDist + ranDist) * sin(angle);
            z = 0; // frand(randRange);
            vx = - vCircular(x,y,z) * sin(angle); // - (v + frand(v/20)) * sin(angle);
            vy =   vCircular(x,y,z)* cos(angle); //  (v + frand(v/20)) * cos(angle);
            vz =   0; // frand(v/20);
            // printf("r = %f AU\n", pow(pow(x,2) + pow(y,2) + pow(z,2), 0.5) * m2au);
            // printf("v = %f\n\n", vCircular(x,y,z));
            reb_simulation_add_fmt(r, "x y z vx vy vz", x, y, z, vx, vy, vz);
        }
        printf("Done!\n");
    }
    
    else {
        printf("Calculating asteroid states ... ");
        char cmdStr1[] = "python3 randAstOrbitGen.py "; 
        char cmdStr2[64];
        sprintf(cmdStr2, "%d", nAsteroids);
        strcat(cmdStr1, cmdStr2);
        system(cmdStr1);
        printf("Done!\n");
        printf("Adding asteroids to simulation ... ");

        f = fopen("asteroidStates.csv", "r");

        if (f == NULL){
            printf("\nError opening the file\n");
            return EXIT_FAILURE;
        }

        while ((line_size = getline(&line_buf, &line_buf_size, f)) != -1){

            // read the file with asteroid states
            sscanf(line_buf, "%lf %lf %lf %lf %lf %lf", &state[0], &state[1], &state[2], &state[3], &state[4], &state[5]);
            if( line_size <= 0 ){
                printf("Reached end of file, or otherwise failed to read. Returned: %i\n", (int)line_size);
                break; //exit the loop
            }

            // add asteroids
            x = state[0];
            y = state[1];
            z = state[2];
            vx = state[3];
            vy = state[4];
            vz = state[5];
            // printf("r = %f AU\n", pow(pow(x,2) + pow(y,2) + pow(z,2),0.5) * m2au);
            // printf("v = %f m/s\n\n", pow(pow(vx,2) + pow(vy,2) + pow(vz,2),0.5));
            reb_simulation_add_fmt(r, "x y z vx vy vz", x, y, z, vx, vy, vz);
            count++;
        }

        fclose(f);
        printf("Done!\n");
    }
    

    printf("Setting up the simulation parameters ... ");
    reb_simulation_move_to_com(r);
    // do funky simulation
    endTime = 86400. * 365 * 100000; // * 1000; // one hundred years in seconds
    int nSnapshots = 10;
    double saveInterval = endTime / nSnapshots;
    reb_simulation_save_to_file_interval(r, "archive.bin", saveInterval);
    r->dt         = 8640000.;
    r->N_active   = 10; // only the planets are not test particles
    r->heartbeat  = heartbeat;
    r->integrator = REB_INTEGRATOR_WHFAST;
    printf("Done!\n");

    printf("Saving the input state ... ");

    FILE *fInput;

    fInput = fopen("input.csv", "w");
    for (int i=0; i<r->N_active + nAsteroids; i++){
        x = r->particles[i].x;
        y = r->particles[i].y;
        z = r->particles[i].z;
        vx = r->particles[i].vx;
        vy = r->particles[i].vy;
        vz = r->particles[i].vz;
        fprintf(fInput, "%f, %f, %f, %f, %f, %f\n", x, y, z, vx, vy, vz);
    }

    fclose(fInput);

    printf("Done!\n");

    printf("Running the simulation ...\n");
    // int nSimulationSteps = 10000;
    // reb_simulation_steps(r, nSimulationSteps);
    reb_simulation_integrate(r, endTime);
    printf("Done!\n");

    /*
        Print positions of asteroids to csv file
    */

   printf("Saving output state ... ");
    
    FILE *fOutput = fopen("output.csv", "w");
    
    for (int i = 0; i < r->N_active + nAsteroids; i++){
        x = r->particles[i].x;
        y = r->particles[i].y;
        z = r->particles[i].z;
        vx = r->particles[i].vx;
        vy = r->particles[i].vy;
        vz = r->particles[i].vz;
        fprintf(fOutput, "%f, %f, %f, %f, %f, %f\n", x, y, z, vx, vy, vz);
    }

    fclose(fOutput);
    
    printf("Done!\n");

    // free the memory of the simulation after being done
    reb_simulation_free(r);

    // run the plotting script
    system("python3 kirkwood.py");

    return EXIT_SUCCESS;
}