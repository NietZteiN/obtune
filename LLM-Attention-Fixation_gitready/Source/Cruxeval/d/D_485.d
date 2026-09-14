import std.math;
import std.typecons;
import std.array;
import std.algorithm;
import std.string;

string f(string tokens) 
{
    auto splitTokens = tokens.split();
    if (splitTokens.length == 2) {
        splitTokens = splitTokens.reverse;
    }
    return format("%-5s %-5s", splitTokens[0], splitTokens[1]);
}
unittest
{
    alias candidate = f;

    assert(candidate("gsd avdropj") == "avdropj gsd  ");
}
void main(){}
