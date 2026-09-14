import std.math;
import std.typecons;
string f(string[] array) 
{
    string s = " ";
    foreach (str; array) {
        s ~= str;
    }
    return s;
}
unittest
{
    alias candidate = f;

    assert(candidate([" ", "  ", "    ", "   "]) == "           ");
}
void main(){}
