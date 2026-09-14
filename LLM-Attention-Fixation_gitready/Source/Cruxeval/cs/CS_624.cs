using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
class Program
{
    public static string F(string text, string character)
    {
        int charIndex = text.IndexOf(character);
        List<char> result = new List<char>();
        if (charIndex > 0)
        {
            result.AddRange(text.Substring(0, charIndex).ToCharArray());
        }
        result.AddRange(character.ToCharArray());
        result.AddRange(text.Substring(charIndex + character.Length).ToCharArray());
        return new string(result.ToArray());
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("llomnrpc"), ("x")).Equals(("xllomnrpc")));
    }

}
