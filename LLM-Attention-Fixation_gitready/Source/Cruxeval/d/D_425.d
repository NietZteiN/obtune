import std.math;
import std.typecons;
import std.string;
import std.array;

string[] f(string a) 
{
    a = a.replace("/", ":");
    auto z = a.split(":");
    return [z.length > 0 ? z[0] : "", 
            z.length > 1 ? ":" : "", 
            z.length > 2 ? z[1..$].join(":") : z.length > 1 ? z[1] : ""];
}
unittest
{
    alias candidate = f;

    assert(candidate("/CL44     ") == ["", ":", "CL44     "]);
}
void main(){}
