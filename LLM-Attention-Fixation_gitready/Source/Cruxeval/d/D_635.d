import std.math;
import std.typecons;
import std.string;
import std.algorithm;

bool f(string text) 
{
    string valid_chars = "-_+./ ";
    text = text.toUpper();
    foreach (c; text)
    {
        if ((c < '0' || c > '9') && (c < 'A' || c > 'Z') && valid_chars.indexOf(c) == -1)
        {
            return false;
        }
    }
    return true;
}
unittest
{
    alias candidate = f;

    assert(candidate("9.twCpTf.H7 HPeaQ^ C7I6U,C:YtW") == false);
}
void main(){}
