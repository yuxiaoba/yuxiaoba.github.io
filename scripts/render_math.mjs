import fs from 'node:fs';
import path from 'node:path';
import { load } from 'cheerio';
import katex from 'katex';
const root = path.resolve(process.argv[2]);
const htmlFiles = dir => fs.readdirSync(dir, {withFileTypes:true}).flatMap(e => e.isDirectory() ? htmlFiles(path.join(dir,e.name)) : e.name.endsWith('.html') ? [path.join(dir,e.name)] : []);
let count = 0;
for (const file of htmlFiles(root)) {
  const original=fs.readFileSync(file,'utf8');
  const $=load(original);
  let changed=false;
  $('script[type^="math/tex"]').each((_,el)=>{
    const tex=$(el).text();
    const displayMode=($(el).attr('type')||'').includes('mode=display');
    const rendered=katex.renderToString(tex,{displayMode,throwOnError:true,trust:false,strict:'warn',output:'htmlAndMathml'});
    $(el).replaceWith(rendered);count++;changed=true;
  });
  // kramdown's MathJax engine emits delimiters as text in this Jekyll version.
  const escapeText=value=>value.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
  const nodes=$('.article-body').find('*').addBack().contents().filter((_,el)=>el.type==='text').toArray();
  for(const el of nodes){
    if($(el).parents('pre,code,script,style,.katex').length)continue;
    const value=el.data||'';const regex=/\\\[([\s\S]*?)\\\]|\\\(([\s\S]*?)\\\)/g;
    let match,last=0,parts=[];
    while((match=regex.exec(value))){
      parts.push(escapeText(value.slice(last,match.index)));
      parts.push(katex.renderToString(match[1]??match[2],{displayMode:match[1]!==undefined,throwOnError:true,trust:false,strict:'warn',output:'htmlAndMathml'}));
      last=regex.lastIndex;count++;
    }
    if(parts.length){parts.push(escapeText(value.slice(last)));$(el).replaceWith(parts.join(''));changed=true;}
  }
  // Code samples containing literal Liquid are restored only after Jekyll has run.
  $('pre code, code').each((_,el)=>{
    const value=$(el).text();
    const decoded=value.replaceAll('&#123;&#123;','{{').replaceAll('&#123;%','{%');
    if(value!==decoded){$(el).text(decoded);changed=true;}
  });
  if(changed) fs.writeFileSync(file,$.html());
}
const vendor=path.join(root,'assets/vendor/katex');
fs.mkdirSync(vendor,{recursive:true});
fs.copyFileSync('node_modules/katex/dist/katex.min.css',path.join(vendor,'katex.min.css'));
fs.cpSync('node_modules/katex/dist/fonts',path.join(vendor,'fonts'),{recursive:true});
fs.copyFileSync('node_modules/katex/LICENSE',path.join(vendor,'LICENSE'));
console.log(`Rendered ${count} math expressions with local KaTeX assets.`);
