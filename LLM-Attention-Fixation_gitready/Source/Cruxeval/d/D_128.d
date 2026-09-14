import std.math;
import std.typecons;
import std.string;

string f(string text) 
{
    string odd = "";
    string even = "";
    foreach(i, c; text) {
        if (i % 2 == 0) {
            even ~= c;
        } else {
            odd ~= c;
        }
    }
    return even ~ toLower(odd);
}
unittest
{
    alias candidate = f;

    assert(candidate("Mammoth") == "Mmohamt");
}
void main(){}
