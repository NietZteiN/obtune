import std.math;
import std.typecons;
import std.ascii;
string f(string phrase) 
{
    string result = "";
    foreach (char i; phrase)
    {
        if (!isLower(i))
        {
            result ~= i;
        }
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate("serjgpoDFdbcA.") == "DFA.");
}
void main(){}
