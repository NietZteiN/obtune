import std.math;
import std.typecons;
import std.string;

string f(long num, string name) 
{
    return "quiz leader = %s, count = %d".format(name, num);
}
unittest
{
    alias candidate = f;

    assert(candidate(23L, "Cornareti") == "quiz leader = Cornareti, count = 23");
}
void main(){}
