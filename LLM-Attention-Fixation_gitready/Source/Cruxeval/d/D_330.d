import std.math;
import std.typecons;
string f(string text) 
{
    string ans;
    foreach (char c; text)
    {
        if (c >= '0' && c <= '9')
        {
            ans ~= c;
        }
        else
        {
            ans ~= ' ';
        }
    }
    return ans;
}
unittest
{
    alias candidate = f;

    assert(candidate("m4n2o") == " 4 2 ");
}
void main(){}
