using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
class Program
{
    public static bool F(string text, string character)
    {
        return text.Count(c => c.ToString() == character) % 2 != 0;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("abababac"), ("a")) == (false));
    }

}
