import std.string;

string f(string text) 
{
    text = text.replace("1", ".");
    text = text.replace("0", "1");
    text = text.replace(".", "0");
    return text;
}
unittest
{
    alias candidate = f;

    assert(candidate("697 this is the ultimate 7 address to attack") == "697 this is the ultimate 7 address to attack");
}
void main(){}
