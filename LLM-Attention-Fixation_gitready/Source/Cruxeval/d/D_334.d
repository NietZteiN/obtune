import std.math;
import std.typecons;
import std.array;

string f(string a, string[] b) 
{
    return b.join(a);
}
unittest
{
    alias candidate = f;

    assert(candidate("00", ["nU", " 9 rCSAz", "w", " lpA5BO", "sizL", "i7rlVr"]) == "nU00 9 rCSAz00w00 lpA5BO00sizL00i7rlVr");
}
void main(){}
