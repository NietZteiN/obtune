import std.math;
import std.typecons;

long f(string val, string text) 
{
    long[] indices;
    foreach (index; 0 .. text.length)
    {
        if (text[index] == val[0]) // Compare single characters
        {
            indices ~= index;
        }
    }
    
    if (indices.length == 0) // Check if indices array is empty
    {
        return -1;
    }
    else
    {
        return indices[0];
    }
}
unittest
{
    alias candidate = f;

    assert(candidate("o", "fnmart") == -1L);
}
void main(){}
