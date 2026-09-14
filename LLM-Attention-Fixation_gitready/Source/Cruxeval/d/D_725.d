import std.math;
import std.typecons;

long f(string text) 
{
    string[] result_list = ["3", "3", "3", "3"];
    if (result_list.length > 0) {
        result_list.length = 0;
    }
    return text.length;
}
unittest
{
    alias candidate = f;

    assert(candidate("mrq7y") == 5L);
}
void main(){}
