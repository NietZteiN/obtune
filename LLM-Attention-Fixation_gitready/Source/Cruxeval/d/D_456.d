import std.math;
import std.typecons;
import std.string;

string f(string s, long tab) 
{
    string tabString = "";
    for (int i = 0; i < tab; i++) {
        tabString ~= " ";
    }
    return s.replace("\t", tabString);
}
unittest
{
    alias candidate = f;

    assert(candidate("Join us in Hungary", 4L) == "Join us in Hungary");
}
void main(){}
