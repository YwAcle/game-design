import {SCENES} from '../shared/scenes.js';
export function initSceneCatalog(){
  const grid=document.querySelector('.journey-grid');grid.replaceChildren();
  for(const [index,[id,scene]] of Object.entries(SCENES).entries()){
    const card=document.createElement('a');card.className='journey-card';card.href=scene.url;card.setAttribute('aria-label','走进'+scene.name);
    const image=document.createElement('img');image.src=`assets/${id}.webp`;image.alt=scene.name+'的三维场景实景';image.loading='lazy';card.append(image);
    const number=document.createElement('span');number.className='journey-index';number.textContent=String(index+1).padStart(2,'0')+' / '+scene.english;card.append(number);
    const badge=document.createElement('span');badge.className='journey-badge';badge.textContent='可自由漫游';card.append(badge);
    const copy=document.createElement('span');copy.className='journey-copy';
    for(const [tag,text] of [['small',scene.line],['strong',scene.name],['span',scene.description],['b','走进这里 ↗']]){const node=document.createElement(tag);node.textContent=text;copy.append(node);}
    card.append(copy);grid.append(card);
    if(['hall','arena'].includes(id))continue;
    const option=document.createElement('option');option.value=id;option.textContent=scene.name;document.querySelector('#scene-input').append(option);
    const label=document.createElement('label'),input=document.createElement('input'),cover=document.createElement('img');
    input.type='radio';input.name='cover';input.value=id;cover.src=`assets/${id}.webp`;cover.alt=scene.name;label.append(input,cover);document.querySelector('.cover-picker').append(label);
  }
}
