import std.math;
import std.typecons;
import std.string;

string f(string string) 
{
    if (string[0..4] != "Nuva")
    {
        return "no";
    }
    else
    {
        return string.strip();
    }
}
unittest
{
    alias candidate = f;

    assert(candidate("Nuva?dlfuyjys") == "Nuva?dlfuyjys");
}
void main(){}
