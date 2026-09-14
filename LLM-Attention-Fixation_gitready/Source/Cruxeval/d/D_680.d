import std.math;
import std.typecons;
import std.string;

string f(string text) 
{
    string letters = "";
    foreach (i, c; text)
    {
        if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9'))
        {
            letters ~= c;
        }
    }
    return letters;
}
unittest
{
    alias candidate = f;

    assert(candidate("we@32r71g72ug94=(823658*!@324") == "we32r71g72ug94823658324");
}
void main(){}
