import std.math;
import std.typecons;
import std.string;

long f(string haystack, string needle) 
{
    for (long i = haystack.indexOf(needle); i >= 0; i--) {
        if (haystack[i .. $] == needle) {
            return i;
        }
    }
    return -1;
}
unittest
{
    alias candidate = f;

    assert(candidate("345gerghjehg", "345") == -1L);
}
void main(){}
