import std.math;
import std.typecons;

string[] f(string[] list_, long num) 
{
    string[] temp;
    foreach (i; list_) {
        string newStr;
        for (size_t j = 0; j < num / 2; j++) {
            newStr ~= i ~ ",";
        }
        temp ~= newStr;
    }
    return temp;
}
unittest
{
    alias candidate = f;

    assert(candidate(["v"], 1L) == [""]);
}
void main(){}
