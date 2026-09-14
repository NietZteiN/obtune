import std.math;
import std.typecons;
import std.string;
import std.algorithm;
import std.array;

string f(string[] simpons) 
{
    string pop;
    while (!simpons.empty) {
        pop = simpons.back;
        simpons.popBack();
        if (pop == pop.capitalize) {
            return pop;
        }
    }
    return pop;
}
unittest
{
    alias candidate = f;

    assert(candidate(["George", "Michael", "George", "Costanza"]) == "Costanza");
}
void main(){}
