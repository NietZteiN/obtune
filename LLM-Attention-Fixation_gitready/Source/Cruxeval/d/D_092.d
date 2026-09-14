import std.math;
import std.typecons;
import std.conv;

bool f(string text) 
{
    foreach (c; text)
    {
        int codePoint = cast(int) c;
        if (codePoint < 0 || codePoint > 127)
        {
            return false;
        }
    }
    return true;
}
unittest
{
    alias candidate = f;

    assert(candidate("wW의IV]HDJjhgK[dGIUlVO@Ess$coZkBqu[Ct") == false);
}
void main(){}
