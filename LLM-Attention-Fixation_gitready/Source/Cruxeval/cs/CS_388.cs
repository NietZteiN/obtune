using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string characters) {
        var characterList = characters.ToCharArray().ToList();
        characterList.Add(' ');
        characterList.Add('_');

        int i = 0;
        while (i < text.Length && characterList.Contains(text[i]))
        {
            i++;
        }

        return text.Substring(i);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("2nm_28in"), ("nm")).Equals(("2nm_28in")));
    }

}
