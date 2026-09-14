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
        if (text.Contains(character))
        {
            var textList = text.Split(character).Select(t => t.Trim()).Where(t => !string.IsNullOrEmpty(t)).ToList();
            if (textList.Count > 1)
            {
                return true;
            }
        }
        return false;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("only one line"), (" ")) == (true));
    }

}
