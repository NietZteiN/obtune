import std.math;
import std.typecons;
import std.conv;

string f(long temp, long timeLimit) 
{
    long s = timeLimit / temp;
    long e = timeLimit % temp;
    return [to!string(e) ~ " oC", to!string(s) ~ " " ~ to!string(e)][s > 1];
}
unittest
{
    alias candidate = f;

    assert(candidate(1L, 1234567890L) == "1234567890 0");
}
void main(){}
