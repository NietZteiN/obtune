import std.math;
import std.typecons;
string f(long num) 
{
    if (0 < num && num < 1000 && num != 6174) {
        return "Half Life";
    }
    return "Not found";
}
unittest
{
    alias candidate = f;

    assert(candidate(6173L) == "Not found");
}
void main(){}
