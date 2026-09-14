import std.math;
import std.typecons;
import std.stdio;
import std.string;
import std.algorithm;

string[] f(string[] lines) 
{
    size_t maxLength = 0;
    foreach (line; lines)
    {
        maxLength = max(line.length, maxLength);
    }
    foreach (ref line; lines)
    {
        line = line.center(maxLength);
    }
    return lines;
}
unittest
{
    alias candidate = f;

    assert(candidate(["dZwbSR", "wijHeq", "qluVok", "dxjxbF"]) == ["dZwbSR", "wijHeq", "qluVok", "dxjxbF"]);
}
void main(){}
