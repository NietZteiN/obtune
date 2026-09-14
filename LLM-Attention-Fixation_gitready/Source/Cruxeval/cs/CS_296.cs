using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string url) {
        return url.StartsWith("http://www.") ? url.Substring("http://www.".Length) : url;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("https://www.www.ekapusta.com/image/url")).Equals(("https://www.www.ekapusta.com/image/url")));
    }

}
