using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
class Program
{
    static string F(string character)
    {
        if (!"aeiouAEIOU".Contains(character))
        {
            return null;
        }
        if ("AEIOU".Contains(character))
        {
            return character.ToLower();
        }
        return character.ToUpper();
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("o")).Equals(("O")));
    }

}
