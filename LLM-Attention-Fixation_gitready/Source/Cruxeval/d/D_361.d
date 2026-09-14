import std.math;
import std.typecons;
import std.array;
import std.string;

long f(string text) 
{
    auto tokens = text.split(':');
    // Check if there is at least one token before counting '#'
    if (tokens.length > 0) {
        return tokens[0].count('#');
    }
    return 0;
}
unittest
{
    alias candidate = f;

    assert(candidate("#! : #!") == 1L);
}
void main(){}
