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
        int length = text.Length;
        int index = -1;
        for (int i = 0; i < length; i++)
        {
            if (text[i] == character[0])
            {
                index = i;
            }
        }
        if (index == -1)
        {
            index = length / 2;
        }
        List<char> newText = text.ToList();
        newText.RemoveAt(index);
        return new string(newText.ToArray());
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("o horseto"), ("r")).Equals(("o hoseto")));
    }

}
