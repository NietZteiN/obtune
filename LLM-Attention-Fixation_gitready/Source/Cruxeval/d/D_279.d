import std.math;
import std.typecons;
import std.string;

string f(string text) 
{
    string ans = "";
    while (text != "") {
        auto x = text.split('(')[0];
        auto sep = text.split('(')[1];
        text = text.split('(')[2];
        sep = sep.replace("(", "|");
        ans = x ~ sep ~ ans;
        ans = ans ~ text[0] ~ ans;
        text = text[1..$];
    }
    return ans;
}
unittest
{
    alias candidate = f;

    assert(candidate("") == "");
}
void main(){}
