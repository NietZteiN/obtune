import std.math;
import std.typecons;
import std.array;

string f(string text, string use) 
{
    return text.replace(use, "");
}
unittest
{
    alias candidate = f;

    assert(candidate("Chris requires a ride to the airport on Friday.", "a") == "Chris requires  ride to the irport on Fridy.");
}
void main(){}
